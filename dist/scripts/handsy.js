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
  console.log(results);
  if (results.multiHandLandmarks) {
    
    for (const landmarks of results.multiHandLandmarks) {
      
      // Goes directly to pointer finger... Have to choose one.
      pointerFinger = landmarks[8]

      x = parseFloat(pointerFinger.x.toPrecision(8));
      y = parseFloat(pointerFinger.y.toPrecision(8));

      // x: Math.floor((1 - x) * viewportWidth),
      handPoint = {
        x: Math.floor((x) * viewportWidth),
        y: Math.floor((y) * viewportHeight)
      };

      // console.log(pointerFinger);
      // console.log(parseFloat(pointerFinger.x.toPrecision(8)), parseFloat(pointerFinger.y.toPrecision(8)));
      // console.log((1 - x), (1 - y), viewportHeight, viewportWidth);
      // console.log(handPoint);
      
    }
  }
  //canvasCtx.restore();
}

const hands = new Hands({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
}});
hands.setOptions({
  staticImageMode: 1,
  maxNumHands: 1,
  modelComplexity: 0,
  minDetectionConfidence: 0.5,
  canned_gestures_classifier_options: ['Pointing_Up', 'Closed_Fist'],
  minTrackingConfidence: 0.5
});
hands.onResults(onResults);

// TODO: Work on mobile...
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await hands.send({image: videoElement});
  },
  width: 1280,
  height: 720
});
camera.start();