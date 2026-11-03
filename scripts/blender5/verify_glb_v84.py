"""Independent GLB structure verifier. Can run without Blender."""
import json,struct,sys,hashlib
from pathlib import Path

def read_document(path):
    path=Path(path)
    with path.open('rb') as f:
        raw=f.read(20)
        if len(raw)!=20:raise ValueError('Incomplete GLB header')
        magic,version,total,size,kind=struct.unpack('<4sIII4s',raw)
        if magic!=b'glTF' or version!=2 or total!=path.stat().st_size or kind!=b'JSON':
            raise ValueError('Invalid glTF 2.0 GLB')
        payload=f.read(size)
        if len(payload)!=size:raise ValueError('Incomplete GLB JSON')
        doc=json.loads(payload.decode('utf-8'))
    return doc

def verify_document(doc):
    nodes=doc.get('nodes',[])
    names=[n.get('name') for n in nodes]
    marker=[i for i,n in enumerate(names) if n=='MuzzleTip_R']
    socket=[i for i,n in enumerate(names) if n=='weapon_socket.R']
    if len(marker)!=1 or len(socket)!=1:
        raise ValueError('Unique exported anchor and original weapon socket required')
    links={}
    for pi,node in enumerate(nodes):
        for ch in node.get('children',[]):
            if not isinstance(ch,int) or not 0<=ch<len(nodes) or ch in links:
                raise ValueError('Invalid or multiply-parented hierarchy')
            links[ch]=pi
    current=marker[0];ancestry=set()
    while current in links:
        current=links[current]
        if current in ancestry:raise ValueError('Cyclic hierarchy')
        ancestry.add(current)
    if socket[0] not in ancestry:
        raise ValueError('Muzzle marker not attached to original weapon socket hierarchy')
    if not any(len(s.get('joints',[]))==15 for s in doc.get('skins',[])):
        raise ValueError('Original 15 joints not preserved')
    if len(doc.get('animations',[]))<6:
        raise ValueError('Original six animation clips not preserved')
    for n in ('PrimaryCannon_energy_bore','PrimaryCannon_outer_barrel'):
        if n not in names:raise ValueError('Missing original cannon component '+n)
    return {'schema':'taipei-mecha-v84-glb-structure','anchor_node':marker[0],
       'socket_node':socket[0],'anchor_attached_to_socket':True,
       'animation_count':len(doc['animations']),'original_skin_joint_count':15}

def verify_file(path):
    r=verify_document(read_document(path))
    r['sha256']=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return r

if __name__=='__main__':print(json.dumps(verify_file(sys.argv[1]),indent=2))
