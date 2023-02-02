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
var handPoint = undefined;

points = [];


$(document).ready(function(){
	document.getElementById('bg').height = $(document).height();
	document.getElementById('bg').width = $(document).width();
  

	var isMobile = false; //initiate as false
	// device detection
	if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
			|| /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) { 
			isMobile = true;
	}
	if(!isMobile){
		onmousemove = function(e){
			mouseX = e.clientX;
			mouseY = e.clientY
		}
	}
	else{
		const src = document.getElementById("bg");
		const canvas = document.getElementById("canvas");	
	}

	
	for(var i = 0; i < 20; i++){
		
    let yCord = Math.floor($(document).height() / 20) * i;
		let xCord = ( i % 2 == 0 ? Math.floor($(document).width() / 3) : Math.floor($(document).width() * 2 / 3) ) ;


		// We have to round each coord before we draw anything.
		points.push([xCord, yCord]);

    animation = new animatedLine(xCord, yCord, "#0F5791", i);
		animation.init();

	}

});

function animatedLine(startx, starty, colorStr, id){
	// these should be passed into the object.
	this.curpointX = startx,
	this.curpointY = starty,
	this.colorHex = colorStr;
	this.id = id;

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
		console.log("Here starting the thing to move.");
		window.requestAnimationFrame(step);
	}

	this.start = undefined;
	this.previousTimeStamp = undefined;

	function step(timestamp) {

		if (this.start === undefined) {
			start = timestamp;
		}

		if (this.previousTimeStamp !== timestamp) {
			self.animate();
			window.requestAnimationFrame(step);
			previousTimeStamp = timestamp;
		}
	}

	this.animate = function() {

		endpointx = this.endpointx;
		endpointy = this.endpointy;

    this.startpointy = this.curposy;
		this.startpointx = this.curposx;
		
		// What is going on here?
		if(endpointx != this.curposx){
			this.curposx += (endpointx > this.curposx ? 1 : -1);
		}
		if(endpointy != this.curposy){
			this.curposy += (endpointy > this.curposy ? 1 : -1);
		}
		
		if (this.curposx == endpointx && this.curposy == endpointy){
			let res = this.getXY();
			this.setAnimationVariables(res.x, res.y);
			return false;
		}

	  this.drawShape(this.curposx, this.curposy, this.colorHex);

	}

	this.drawShape = function(tendpointx, tendpointy, color){
	    let canvas = document.getElementById('bg');
	    let ctx = canvas.getContext("2d");
			
			ctx.strokeStyle = '#FF0000';
			if(handPoint != undefined){
				ctx.beginPath();
				ctx.arc(handPoint.x, handPoint.y, 5, 0, 2 * Math.PI);
				ctx.stroke();
			}
			
			ctx.strokeStyle = color;
	    ctx.globalAlpha = 0.2;
			
			n = Date.now()
			
			if(this.timestamp == undefined)
				this.timestamp = Date.now();
			
			let i = 0;
			let iterations = 0;

			if((n - this.timestamp) < 10)
				iterations = 1;
			else
				iterations = Math.ceil((n - this.timestamp) / 10);

			// start drawing.
			// TODO: something is off with the randomness direction
			ctx.beginPath();
			while(i < iterations){
				ctx.moveTo(this.startpointx ,this.startpointy);
				ctx.lineTo(tendpointx, tendpointy);
				
				this.startpointx = tendpointx;
				this.startpointy = tendpointy;
				let newPoint = this.getXY();

				this.setAnimationVariables(newPoint.x, newPoint.y);
				
				// reset the point if the point is the same as a prev point.
				tendpointx = newPoint.x;
				tendpointy = newPoint.y;
				i++;
			}
	    
			
			// TODO: create a function to grab a new point.
	    ctx.stroke();
			
			// TODO: We have to figure out how to optimize or dedicate a cpu to this operation.
			// TODO: Also another option is to put the hands detection on another device.
			fps = Date.now() - this.timestamp / 1000
			this.timestamp = Date.now();
	} 

	this.getXY = function(){
		
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
      // pointOfInterest.y = Math.floor($(document).width() / 2)
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
	this.init();

	// Helper function to set variables for animation. 
	// TODO refactor to get rid of some of these variables.
	this.setAnimationVariables = function(newPointX, newPointY){

		// we can check this inside of here. 
		// check the newpoints. Verify its inside the canvas.
		// TODO: verify the new points are not the same as previous points.
		if(newPointY > 0 && newPointX > 0 && newPointY < $(document).height() && newPointX < $(document).width()){
			this.startpointx = this.endpointx;
			this.startpointy = this.endpointy;
			this.curpointX = this.endpointx;
			this.curpointY = this.endpointy;
			this.endpointx = newPointX;
			this.endpointy = newPointY;
		}
		else {
			res = this.getXY();
			this.setAnimationVariables(res.x, res.y);
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

