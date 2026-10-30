const {test}=require('node:test');
const assert=require('node:assert/strict');
const {normalizeProject,languages,speechLocales}=require('../studio-data.js');
const project=(line={})=>({schema_version:'1.0',custom:'keep',character:{id:'auntie',name:'阿姨',consent:'authorized reference'},lines:[{id:'one',text:'Hello',emotion:'開心',strength:0.6,speed:1,language:'en',...line}]});
test('all supported languages survive import/export and preview locale mapping',()=>{
  for(const language of Object.keys(languages)){
    const result=normalizeProject(project({language}));
    assert.equal(result.lines[0].language,language);
    assert.ok(speechLocales[language]);
    assert.deepEqual(normalizeProject(JSON.parse(JSON.stringify(result))),result);
  }
});
test('all Chinese aliases map to canonical emotions instead of natural',()=>{
  const aliases={'自然':'natural','開心':'happy','生氣':'angry','悲傷':'sad','害怕':'afraid','厭惡':'disgusted','憂鬱':'melancholic','驚訝':'surprised','平靜':'calm'};
  for(const [emotion,expected] of Object.entries(aliases))assert.equal(normalizeProject(project({emotion})).lines[0].emotion,expected);
});
test('preserves consent, project metadata and line extensions',()=>{
  const result=normalizeProject(project({customLine:'keep'}));
  assert.equal(result.custom,'keep');assert.equal(result.character.consent,'authorized reference');assert.equal(result.lines[0].customLine,'keep');
});
test('defaults apply only when settings are absent',()=>{
  assert.equal(normalizeProject(project({language:undefined,emotion:undefined})).lines[0].language,'zh');
  assert.equal(normalizeProject(project({language:undefined,emotion:undefined})).lines[0].emotion,'natural');
});
test('invalid settings reject import without changing original project',()=>{
  for(const change of [{language:'fr'},{emotion:'joyful'},{strength:NaN},{speed:Infinity},{text:''},{id:'../bad'}]){
    const obj=project(change), before=structuredClone(obj);
    assert.throws(()=>normalizeProject(obj));assert.deepEqual(obj,before);
  }
  const obj=project();obj.lines.push({...obj.lines[0]});assert.throws(()=>normalizeProject(obj));
  assert.throws(()=>normalizeProject({...project(),lines:[]}));
});
test('malformed JSON types cannot coerce into valid language or emotion',()=>{
  for(const field of ['language','emotion','text','strength','speed']){
    for(const value of [null,[],{},true,false])assert.throws(()=>normalizeProject(project({[field]:value})),`${field}: ${JSON.stringify(value)}`);
  }
  for(const [field,value] of [['language',['en']],['emotion',['開心']],['strength',[0.6]],['speed',[1]],['text',['hello']]])assert.throws(()=>normalizeProject(project({[field]:value})));
  for(const raw of [null,[],true,'hello'])assert.throws(()=>normalizeProject({...project(),lines:[raw]}));
});
