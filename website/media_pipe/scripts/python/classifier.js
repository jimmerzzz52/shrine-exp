loadPyodide
let initPyodide = loadPyodide()
// 
async function main(kw){
  // <!-- This is a copy straight from base.py...  -->
  // <!-- TODO: Figure out how to publish and import it -->
  // Hack!! Use this to convert the file spaces/tabs to double spaces. 
  // https://phrasefix.com/tools/convert-double-space-to-single-space/
  let pyodide = await initPyodide
  await pyodide.loadPackage("pandas")
  await pyodide.loadPackage("numpy")
  await pyodide.runPython(base_python)
  //await pyodide.loadPackage("datetime")

  let classifier = {
    classify: function(xyz_input){
    // TODO: Create the string below... Or input it into the python somehow.
    pyodide.runPython(`
      # TODO: We need to input the dataframe/xyz string from above here...
      g = Gesture()
      print(`+xyz_input+`)
    `);
    }
  }
  return classifier.classify();
}
main();