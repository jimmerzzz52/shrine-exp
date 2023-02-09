const NORTH = 1;
const NORTHEAST = 2;
const EAST = 3;
const SOUTHEAST = 4;
const SOUTH = 5;
const SOUTHWEST = 6; 
const WEST = 7;
const NORTHWEST = 8;
const CANVAS_COUNT = 10;

var mouseX = 0;
var mouseY = 0;
var handPoint = undefined;

var animatedLines = [];

points = [];

onmousemove = function(e){
	mouseX = e.clientX;
	mouseY = e.clientY;
	// console.log("mouse location:", e.clientX, e.clientY)
}

$(document).ready(function(){
	
	// We need to create a bunch of canvas elements to cycle through.
	
	const docHeight = $(document).height();
	const docWidth = $(document).width();
	const disp = document.getElementById('display');

	// TODO: handle resize of page.
	document.getElementById('display').height = docHeight;
	document.getElementById('display').width = docWidth;
	document.getElementById('display').position = 'relative';
	
	for(var i = 0; i < 10; i++){

    let yCord = Math.floor(docHeight / 20 * i);
		let xCord = Math.floor( i % 2 == 0 ? docWidth / 3 : docWidth * 2 / 3 );

		points.push([xCord, yCord]);
		
    animation = new animatedLine(xCord, yCord, "#0F5791", uuidv4());
		animation.init();
		animatedLines.push(animation);

	}

});

function animatedLine(startx, starty, colorStr, id){
	// These should be passed into the object.
	this.curpointX = startx,
	this.curpointY = starty,
	this.colorHex = colorStr;
	this.id = id;

	let self = this;
	this.canvasPointer = 0;

	this.endpointx = this.curpointX;
	this.endpointy = this.curpointY;


	this.init = function() {
		// window.requestAnimationFrame(step);
		const docHeight = $(document).height();
		const docWidth = $(document).width();
		const disp = document.getElementById('display');

		// create the canvas elements.
		for(var i = 0; i < CANVAS_COUNT; i++){
			const canvasElement = document.createElement("canvas");
			canvasElement.id = 'canvas_'+ this.id + '-' + i;
			canvasElement.style.position = 'absolute';
			canvasElement.height = docHeight;
			canvasElement.width = docWidth;
			disp.appendChild(canvasElement);
		}

		setInterval(function () {self.animate();}, 20);
	}

	this.start = undefined;
	this.previousTimeStamp = undefined;

	this.animate = function() {

		let res = this.getRandomNextPoint();
		this.setPointInBounds(res.x, res.y);

		// In case it's the same point...
		if(this.endpointx != this.curpointX){
			this.curpointX += (this.endpointx > this.curpointX ? 1 : -1);
		}
		if(this.endpointy != this.curpointY){
			this.curpointY += (this.endpointy > this.curpointY ? 1 : -1);
		}
		
		if (this.curpointX == this.endpointx && this.curpointY == this.endpointy){
			let res = this.getRandomNextPoint();
			this.setPointInBounds(res.x, res.y);
			return false;
		}

	  this.drawShape();

	}

	this.drawShape = function(){
	    
			this.canvasPointer = ( this.canvasPointer + 1 ) % CANVAS_COUNT;
			
			// clear the old canvas as we cycle through.
			let canvas = document.getElementById('canvas_' + this.id + '-' + this.canvasPointer);
	    let ctx = canvas.getContext("2d");

			ctx.strokeStyle = '#FF0000';
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			
			if(handPoint != undefined){
				ctx.beginPath();
				ctx.arc(handPoint.x, handPoint.y, 5, 0, 2 * Math.PI);
				ctx.stroke();
			}
			
			ctx.strokeStyle = this.colorHex;
	    ctx.globalAlpha = 1;
			
			n = Date.now();
			
			if(this.timestamp == undefined)
				this.timestamp = Date.now();
			
			let i = 0;
			let iterations = 0;

			// if((n - this.timestamp) < 10)
			iterations = 1;
			// else
			// 	iterations = Math.ceil((n - this.timestamp) / 10);

			// start drawing.
			// TODO: something is off with the randomness direction
			ctx.beginPath();

			while(i < iterations){
				
				ctx.moveTo(this.curpointX ,this.curpointY);
				
				let newPoint = this.getRandomNextPoint();
				this.endpointx = newPoint.x;
				this.endpointy = newPoint.y;
				this.setPointInBounds(newPoint.x, newPoint.y);
				ctx.lineTo(this.endpointx, this.endpointy);
				
				i++;

			}
			
			// TODO: create a function to grab a new point.
			
	    ctx.stroke();
			
			// TODO: We have to figure out how to optimize or dedicate a cpu to this operation.
			// TODO: Also another option is to put the hands detection on another device.
			fps = Date.now() - this.timestamp / 1000
			this.timestamp = Date.now();
	} 

	this.getRandomNextPoint = function(){
		
		// calculate the next point with direction and distance.
		var direction = Math.floor(Math.random() * 8) + 1;
		var distance = Math.floor(Math.random() * 10) + 1;

		var newPointY, newPointX;
    
		// Gravitate towards the middle...
    // This will be imporant for interaction... 
    // We want to gravitate towards things.
    if( Math.floor(Math.random() * 4) < 1 ){
      
      let here = {}
      here.x = this.endpointx;
      here.y = this.endpointy;
      
      let pointOfInterest = {}
      // pointOfInterest.x = Math.floor($(document).height() / 2)
      // pointOfInterest.y = Math.floor(docheight / 2)
      pointOfInterest.x = mouseX;
      pointOfInterest.y = mouseY;

			if(handPoint != undefined){
				pointOfInterest.x = handPoint.x;
				pointOfInterest.y = handPoint.y;
			}
			
			// set the direction towards the pointOfInterest.
      direction = this.getDirectionOf(here, pointOfInterest);
    }

		switch(direction){
			case NORTH:
				newPointX = this.endpointx;
				newPointY = this.endpointy - distance;
				break; 
			case NORTHEAST:
				newPointX = this.endpointx + distance;
				newPointY = this.endpointy - distance;
				break;
			case EAST:
				newPointX = this.endpointx + distance;
				newPointY = this.endpointy;
				break; 
			case SOUTHEAST: 
				newPointX = this.endpointx + distance;
				newPointY = this.endpointy + distance;
				break;
			case SOUTH:
				newPointX = this.endpointx;
				newPointY = this.endpointy + distance;
				break;
			case SOUTHWEST:
				newPointX =  this.endpointx - distance;
				newPointY = this.endpointy + distance;
				break;
			case WEST:
				newPointX = this.endpointx - distance;
				newPointY = this.endpointy;
				break;
			case NORTHWEST:
				newPointX = this.endpointx - distance;
				newPointY = this.endpointy - distance;
				break;
		}
		
		newPointX = Math.floor(newPointX);
		newPointY = Math.floor(newPointY);

		return {
			x: newPointX,
			y: newPointY
		}
	}
	// Why am I initializing this on every run??
	// this.init();

	// Helper function to set variables for animation. 
	// TODO refactor to get rid of some of these variables.
	this.setPointInBounds = function(newPointX, newPointY){

		// we can check this inside of here. 
		// check the newpoints. Verify its inside the canvas.
		// TODO: verify the new points are not the same as previous points.
		if(newPointY > 0 && newPointX > 0 && newPointY < $(document).height() && newPointX < $(document).width()){
			this.curpointX = this.endpointx;
			this.curpointY = this.endpointy;
			this.endpointx = newPointX;
			this.endpointy = newPointY;
		}
		else {
			point = this.getRandomNextPoint();
			this.setPointInBounds(point.x, point.y);
		}
	}


	this.getDirectionOf = function(pointA, pointB){
		let direction
		if( pointA.x > pointB.x && pointA.y > pointB.y)
			direction = NORTHWEST
		else if(pointA.x < pointB.x && pointA.y > pointB.y)
			direction = NORTHEAST
		else if(pointA.x > pointB.x && pointA.y < pointB.y)
			direction = SOUTHWEST
		else if(pointA.x < pointB.x && pointA.y < pointB.y)
			direction = SOUTHEAST
		else if(pointA.x == pointB.x && pointA.y > pointB.y)
			direction = SOUTH
		else if(pointA.x == pointB.x && pointA.y < pointB.y)
			direction = NORTH
		else if(pointA.x > pointB.x && pointA.y == pointB.y)
			direction = WEST
		else if(pointA.x < pointB.x && pointA.y == pointB.y)
			direction = EAST
		else
			direction = Math.floor(Math.random() * 8) + 1
	
		return direction;
	}

}

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}