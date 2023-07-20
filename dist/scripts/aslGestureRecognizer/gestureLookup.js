// TODO: Figure out how to index the gestures into a prefix dictionary. 
// Grab the list by ls -1 the scripts/assets/asl folder.
// TODO: Automate this in the build process and build the tree. 
// INstructions to set this up correctly
// Navigate to assets/asl
// cat * > combined.json
// sed -i -e 's/\]/,/g' combined.json
// sed -i -e 's/\[//g' combined.json
// put the contents of the json into the COMBINED variable.

// ls the contents of assets, make sure this is the same order as the above script...
GESTURE_NAMES = ["eight.json","five.json","four.json","nine.json","one.json","seven.json","six.json","ten.json","three.json","two.json","zero.json"];
  
// Massage the combined gestures into the right format.
raw_gestures = []
raw_to_indexed = function(){
    
    for(let i = 0; i < COMBINED_GESTURES.length; i++){
    let pointIndex = i % 21;
    let gestureIndex = 0;

    if(i > 21)
        gestureIndex = (i - pointIndex) / 21;
    
    if( raw_gestures[gestureIndex] == undefined)
        raw_gestures[gestureIndex] = {};
    
    raw_gestures[gestureIndex][pointIndex] = COMBINED_GESTURES[i];
    }
}

// TODO: Hard to explain, we need to have documentation on this.
raw_to_normalized = function(){
    // Take the max and min of the two highest points.
    // Take the max and min of the two left and right.
    
    for( let i = 0; i < raw_gestures.length; i++){
        // get min max
        normalize_item(raw_gestures[i]);
    }
}
// Mutator.
normalize_item(gesture){
    // TODO: Implement infinity, but for now this will do...
    gesture.minX = gesture[0].x;
    gesture.maxX = gesture[0].x;
    gesture.minY = gesture[0].y;
    gesture.maxY = gesture[0].y;

    for(let i = 1; i < gesture.length; i++){
        gesture.minX = Math.min(gesture[i].x, minX)
        gesture.maxX = Math.max(gesture[i].x, maxX)
        gesture.minY = Math.min(gesture[i].y, minY)
        gesture.maxY = Math.max(gesture[i].y, maxY)
    }

    for(let i = 1; i < gesture.length; i++){
        gesture.d_X = gesture[i].x - gesture.minX / (gesture.maxX - gesture.minX)
        gesture.c_Y = gesture[i].y - gesture.minY / (gesture.maxY - gesture.minY)
    }
}
raw_to_indexed()


// Let's figure out the error function.
// TODO: refactor this to be a tree rounded to "zoned" areas. 
// These areas will be rounding zones.
// For now this will be sequential.

function lookupGestureFromPoints(points){

  CONFIG = {} // configure the lookup specifics
   
  // Find the closest point to the current point
  let minDelta = undefined;
  let gestureClosest = 0;
  
  let gesturesError = [];


  // Angulur error
  for(let i = 0; i < raw_gestures.length; i++){
    let overallDelta = 0;
    for(let j = 1; j < points.length - 1; j++){
      let pointDelta = Math.abs(raw_gestures[i][j].angle - points[i].angle)
      overallDelta = pointDelta + overallDelta;
    }
    if(minDelta == undefined || minDelta > overallDelta)
        gestureClosest = i;
    gesturesError[i] = gesturesError
  }

  // Point to Point error. 
  // TODO: Requires normalization of the points themselves.

//   We have to figure out how to normalize here.
//   for(let i = 0; i < gestures.length; i++){
//     let overallDelta = 0;
//     for(let j = 1; j < points.length - 1; j++){
//       let pointDelta = Math.abs(gestures[i][j].angle - points[i].angle)
//       overallDelta = pointDelta + overallDelta;
//     }
//     if(minDelta == undefined || minDelta > overallDelta)
//         gestureClosest = i;
//     gesturesError[i] = gesturesError
//   }

  logger("Closest Gesture is " + GESTURE_NAMES[gestureClosest], 1);
  logger("Gesture Error is " + GESTURE_NAMES[gestureClosest], 2);
}

