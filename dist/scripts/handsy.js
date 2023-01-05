// For some reason. This fails right when we start this.... I dont know why. 
// Something in the other file is not playing nice with this system.



const videoElement = document.getElementsByClassName('input_video')[0];
  //const canvasElement = document.getElementsByClassName('output_canvas')[0];
  //const canvasCtx = canvasElement.getContext('2d');
var viewerWidth = document.width;

let viewportWidth = parseFloat(window.innerWidth);
let viewportHeight = parseFloat(window.innerHeight);

function onResults(results) {
  
  //canvasCtx.save();
  //canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  //canvasCtx.drawImage(
    //  results.image, 0, 0, canvasElement.width, canvasElement.height);
  if (results.multiHandLandmarks) {
    
    // TODO: We have twenty points. We have to create a mapping.
    // var pi = 0;

    for (const landmarks of results.multiHandLandmarks) {
      
      // console.log(landmarks);
      // Should we do an average of the landmarks??
      // Should we randomly go to each section? That would be kind of cool, and most visually appealing.
      for(var i = 0; i < landmarks.length; i++){
        // points[i][0] = landmarks[i].x * document.width;
        // points[i][1] = landmarks[i].y * document.height;
        
        if(i == 0){
          
          
          
          // This is bad... Idk
          // if(landmarks[i].y > 1)
          //   landmarks[i].y = landmarks[i].y - .4
          

          x = parseFloat(landmarks[i].x.toPrecision(8));
          y = parseFloat(landmarks[i].y.toPrecision(8));

          handPoint = {
            x: Math.floor((1 - x) * viewportWidth),
            y: Math.floor((y) * viewportHeight)
          };

          console.log(landmarks[i]);
          // console.log(parseFloat(landmarks[i].x.toPrecision(8)), parseFloat(landmarks[i].y.toPrecision(8)));
          console.log((1 - x), (1 - y), viewportHeight, viewportWidth);
          console.log(handPoint);
          // console.log(iHandPoint, handPoint, viewportWidth, x, y);
        }
      }

      // Get the middle of all of the points...
      
    }
  }
  //canvasCtx.restore();
}

const hands = new Hands({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
}});
hands.setOptions({
  staticImageMod: 1,
  maxNumHands: 1,
  modelComplexity: 0,
  minDetectionConfidence: 0.5,
  // minTrackingConfidence: 0.5
});
hands.onResults(onResults);
// TODO: Play around with these values of width and height.
// TODO: Browser compatibility.
const camera = new Camera(videoElement, {
  onFrame: async () => {
    // console.log("Here.");
    await hands.send({image: videoElement});
  },
  width: 1280,
  height: 720
});
camera.start();