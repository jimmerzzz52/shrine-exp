let logDict = {};
var logger = function(message, id){
  
  
  // set default debounce to one a second
  if(id != undefined){
    nowzen = Date.now();
    
    if(logDict[id] != undefined){
      if(nowzen - logDict[id] > 1000){
        console.log(message)
        logDict[id] = nowzen
      }
    }
    else
      logDict[id] = nowzen
  }
  else
    console.log(message)
}

// _default_uuid = function(){
//   return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
//     (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
//   );
// }