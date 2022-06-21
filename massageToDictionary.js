let fs = require('fs');



let oxfordProverbsTxt = fs.readFileSync('proverbs.txt', {encoding:'utf8', flag:'r'});


// TODO: refactor to use regex instead of split. 
// Because split has to iterate throug the whole string.
let curLetter  = '';
let proverbs = oxfordProverbsTxt.split('').map(
  function(prov){

    let lines = prov.split('\n');

    for(let i = 0; i < lines.length; i++){
      
      let line = lines[i];
      let words = line.split(' ');


      // TODO: Add smarter logic here. We need to support the quote if it's a few words in...
      if(isAllUpperCase(words[0]) == true){
        
        
        if(words[0].length == 1 && line.length == 1){
          console.log("We are at another letter of the alphabet", curLetter);
          curLetter = words[0];
          continue;
        }

        if( words[0].split('')[0] != curLetter){
          
          // TODO: Add smarter logic here...
          console.log("We had to skip this..", curLetter, words[0]);
          continue;
        }

        return line;
      }
    }
  });


function isAllUpperCase(str){
  return str.toUpperCase() === str && str !== str.toLowerCase();
}

console.log(proverbs);
let dict = {};
proverbs.forEach(function(prov){
  dict[prov] = {};
});
fs.writeFile('./dictionary.json', JSON.stringify(dict), err => {
  if (err) {
    console.error(err)
    return
  }
  console.log("file written.");
})
// console.log(isAProverb, proverbLine[0])