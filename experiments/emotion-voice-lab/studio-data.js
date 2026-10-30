/* Shared by the offline editor and Node regression tests. No network access. */
(function(root){
"use strict";
const aliases={"自然":"natural","開心":"happy","生氣":"angry","悲傷":"sad","害怕":"afraid","厭惡":"disgusted","憂鬱":"melancholic","驚訝":"surprised","平靜":"calm"};
const languages={zh:"中文",en:"English",ja:"日本語",es:"Español",ar:"العربية"};
const speechLocales={zh:"zh-TW",en:"en-US",ja:"ja-JP",es:"es-ES",ar:"ar"};
const validId=value=>typeof value==="string"&&/^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/.test(value);
const isObject=value=>value!==null&&typeof value==="object"&&!Array.isArray(value);
function numericSetting(value,name){
  if(!["number","string"].includes(typeof value)||(typeof value==="string"&&!value.trim()))throw new Error(name+"必須為數字");
  return Number(value);
}
function normalizeProject(obj){
  if(!isObject(obj)||!isObject(obj.character)||!validId(obj.character.id)||!Array.isArray(obj.lines)||!obj.lines.length)throw new Error("需要有效角色 ID 與非空台詞");
  const ids=new Set();
  const lines=obj.lines.map(raw=>{
    if(!isObject(raw)||!validId(raw.id)||ids.has(raw.id))throw new Error("台詞 ID 無效或重複");
    ids.add(raw.id);
    const emotion=raw.emotion===undefined?"natural":raw.emotion;
    const language=raw.language===undefined?"zh":raw.language;
    if(typeof emotion!=="string")throw new Error("情緒必須為文字");
    if(typeof language!=="string"||!Object.hasOwn(languages,language))throw new Error("不支援的語言");
    if(typeof raw.text!=="string")throw new Error("台詞內容必須為文字");
    const line={...raw,text:raw.text.trim(),emotion:Object.hasOwn(aliases,emotion)?aliases[emotion]:emotion,strength:numericSetting(raw.strength===undefined?0.6:raw.strength,"情緒強度"),speed:numericSetting(raw.speed===undefined?1:raw.speed,"語速"),language};
    if(!Object.values(aliases).includes(line.emotion))throw new Error("未知情緒："+emotion);
    if(!line.text||line.text.length>2000)throw new Error("台詞長度必須在 1 到 2000 字元");
    if(!Number.isFinite(line.strength)||line.strength<0.1||line.strength>1)throw new Error("情緒強度超出範圍");
    if(!Number.isFinite(line.speed)||line.speed<0.75||line.speed>1.33)throw new Error("語速超出範圍");
    return line;
  });
  return {...obj,character:{...obj.character},lines};
}
const api={normalizeProject,languages,speechLocales};
if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.StudioData=api;
})(globalThis);
