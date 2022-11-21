NORTH = 1,
NORTHEAST = 2;
EAST = 3;
SOUTHEAST = 4;
SOUTH = 5;
SOUTHWEST = 6; 
WEST = 7;
NORTHWEST = 8;
var mouseX = 0;
var mouseY = 0;



$(document).ready(function(){
	document.getElementById('bg').height = $(document).height();
	document.getElementById('bg').width = $(document).width();
  
  onmousemove = function(e){
    mouseX = e.clientX;
    mouseY = e.clientY
  }

	// ranomize the spot.


	for(var i = 0; i < 12; i++){
		
    yCord = Math.floor($(document).height() / 12) * i;
		xCord = ( i % 2 == 0 ? Math.floor($(document).width() / 3) : Math.floor($(document).width() * 2 / 3) ) ;
		
    animation = new animatedLine(xCord, yCord, "#0F5791");
		animation.init();
	}

});

function animatedLine(startx, starty, colorStr){
	// these should be passed into the object.
	this.curpointX = startx,
	this.curpointY = starty,
	this.colorHex = colorStr;

	var self = this;
	// Lets get rid of one of these position variables.
	this.startpointx = this.curpointX;
	this.startpointy = this.curpointY;
	this.curposx = this.curpointX;
	this.curposy = this.curpointY;
	this.endpointx = this.curpointX;
	this.endpointy = this.curpointY;
	this.myinterval = {};

	this.init = function() {
	   	this.myinterval = setInterval( function() { self.animate(self.endpointx,self.endpointy);}, 1);
	}

	this.animate = function(endpointx, endpointy) {
		// TODO: Document.
    this.startpointy = this.curposy;
		this.startpointx = this.curposx;
		if (this.curposx == endpointx && this.curposy == endpointy){
			this.drawLine();
			return false;
		}
		else if(endpointx != this.curposx && endpointy != this.curposy){
			// this will screw up if we have half pixel somewhere. ( will always be diagnol)
			this.curposy += (endpointy > this.curposy ? 1 : -1);			
			this.curposx += (endpointx > this.curposx ? 1 : -1);
		}
		else if(endpointx != this.curposx){
			this.curposx += (endpointx > this.curposx ? 1 : -1);
		}
		else if(endpointy != this.curposy){
			this.curposy += (endpointy > this.curposy ? 1 : -1);
		}
		else{
			console.log("We have a problem");
		}
	    this.drawShape(this.curposx, this.curposy, this.colorHex);
	}

	this.drawShape = function(tendpointx, tendpointy, clor){
	    var canvas = document.getElementById('bg');
	    var ctx = canvas.getContext('2d');

	    ctx.strokeStyle = clor;
	    ctx.globalAlpha = 0.2;
	    ctx.beginPath();
	    ctx.moveTo(this.startpointx ,this.startpointy );
	    ctx.lineTo(tendpointx,tendpointy);
	    ctx.stroke();
	} 

	this.drawLine = function(flagDirection){
		
		clearInterval(this.myinterval);

		// calculate the next point with direction and distance.
		var direction = Math.floor(Math.random() * 8) + 1;
		var distance = Math.floor(Math.random() * 10) + 1;

		var newPointY, newPointX;


    // Gravitate towards the middle... 
    // This will be imporant for interaction... 
    // We want to gravitate towards things.
    if( Math.floor(Math.random() * 4) < 1 ){
    // if(true){
      
      let here = {}
      here.x = this.endpointx;
      here.y = this.endpointy;
      
      let pointOfInterest = {}
      pointOfInterest.x = Math.floor($(document).height() / 2)
      pointOfInterest.y = Math.floor($(document).width() / 2)
      pointOfInterest.x = mouseX;
      pointOfInterest.y = mouseY;

      // console.log(pointOfInterest);

      // set the direction towards the pointOfInterest.
      direction = getDirectionOf(here, pointOfInterest);
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
    this.setAnimationVariables(newPointX, newPointY);
	}
	this.init();

	// Helper function to set variables for animation. 
	// TODO refactor to get rid of some of these variables.
	this.setAnimationVariables = function(newPointX, newPointY){

		// we can check this inside of here. 
		// check the newpoints. Verify its inside the canvas.
		if(newPointY > 0 && newPointX > 0 && newPointY < $(document).height() && newPointX < $(document).width()){
			this.startpointx = this.endpointx;
			this.startpointy = this.endpointy;
			this.curpointX = this.endpointx;
			this.curpointY = this.endpointy;
			this.endpointx = newPointX;
			this.endpointy = newPointY;			
		}
		else {
			this.drawLine();
		}
	}
}

function getDirectionOf(pointA, pointB){
  let direction
  // TODO: Add N,E,S,W currently gravitating slighly north... Because I am lazy...
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