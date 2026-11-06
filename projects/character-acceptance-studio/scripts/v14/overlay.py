"""Replace body curves while retaining each original travel-root sampler verbatim."""
import copy
from v07.overlay import ClipOverlay

class BodyOverlay(ClipOverlay):
    def replace_body(self, name, times, frames):
        root = next(i for i,n in enumerate(self.doc['nodes']) if n.get('name') == 'StudioTravelRoot_v11')
        assert all(root not in f for f in frames), 'Body export must not replace travel'
        original = copy.deepcopy(next(a for a in self.doc['animations'] if a['name'] == name))
        self.replace_clip(name, times, frames)
        target = next(a for a in self.doc['animations'] if a['name'] == name)
        for channel in original['channels']:
            if channel['target']['node'] != root: continue
            sampler = original['samplers'][channel['sampler']]
            channel['sampler'] = len(target['samplers'])
            target['samplers'].append(sampler)
            target['channels'].append(channel)
