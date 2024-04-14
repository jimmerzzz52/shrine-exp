function normalizeHand(points){
 
  
  // We calculate the angle to the hand base.
  // 0-1-2-3-4
  // 0-5-6-7-8
  // 0-9-10-11-12
  // 0-13-14-15-16
  // 0-17-18-19-20
  // We create a mapping from the above.
  pointToMap = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 0,
    6: 5,
    7: 6,
    8: 7,
    9: 0,
    10: 9,
    11: 10,
    12: 11,
    13: 0,
    14: 13,
    15: 14,
    16: 15,
    17: 0,
    18: 17,
    19: 18,
    20: 19
  }
  thisIsGesture = true;
  for(var i = 1; i < points.length; i++){
    
    let pointBefore = points[pointToMap[i]];
    let point = points[i];
    let deltaX = pointBefore.x - point.x;
    let deltaY = pointBefore.y - point.y;
    let radians = Math.atan2(deltaY, deltaX);
    
    let angle = radians * (180 / Math.PI);

    // TODO: Figure out how to iterate 
    // through the angles to find the right pose.
    point.angle = angle;
    
    // TODO: figure out the "frozen limb bug". A bug where a gesture is better when a limb is frozen
    
    // TODO: Figure out z angle.
    
  }
}