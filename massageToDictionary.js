// TODO: refactor to use prefix tree instead of proverb dictionary.
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

let prefixTree = {};
let dict = {};

proverbs.forEach(function(prov){
  
  
  if(prov != undefined){

    dict[prov.toLowerCase()] = {};

    let words = prov.split(' ')

    let curPrefixBranch = prefixTree;
    
    for(var i = 0; i < words.length; i++){
      
      // TODO: Remove Grammer, Split on space. B/C of extra stuff oxford throws in there...
      let curWord = words[i];
      if(curPrefixBranch[curWord] == undefined)
        curPrefixBranch[curWord] = {};

      if(i == words.length - 1)
        curPrefixBranch[curWord].end = true;
      
      curPrefixBranch = curPrefixBranch[curWord];
    }
  }

});




fs.writeFile('./dist/proverbsDictionary.js', "var proverbs = " + JSON.stringify(dict), err => {
  if (err) {
    console.error(err)
    return
  }
  console.log("file written.");
})

fs.writeFile('./dist/proverbsPrefixTree.js', "var proverbPrefixTree = " + JSON.stringify(prefixTree), err => {
  if (err) {
    console.error(err)
    return
  }
  console.log("file written.");
})