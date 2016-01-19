"use strict";
//Global namespace utilities (common functions used everywhere and some class inheritance stuff)

//COMMON FUNCTIONALITY
function isDef(o)
{
	return !(typeof o === "undefined" || o === null);
}

//jQUERY ADDITIONS
//formVal returns the value of a form. Most val() functions returns/sets value
//checkbox val() doesn't so we go it with true/false
$.prototype.formVal = function(setTo)
{
	if(this.length > 1)
	{
		if(isDef(setTo))
		{
			this.jEach(function(idx,jEl){jEl.formVal(setTo);});
			return null;
		}
		else
		{
			return this.first().formVal(setTo);
		}
	}
	else if(this.is("input[type='checkbox']"))
	{
		if(isDef(setTo))
			return this.prop("checked", setTo);
		else
			return this.prop("checked");
	}
	else
	{
		if(isDef(setTo))
			return this.val(setTo);
		else
			return this.val();
	}
};
//Calls each with every element as a jQuery object
$.prototype.jEach = function(func)
{
	this.each(function(idx, el){func(idx,$(el));});
};
//Extend properties from extender to extendee if keys exist in filter
$.extendSelective = function(extendee, extender, filter)
{
	for(var key in extender)
		if(filter.indexOf(key) != -1 && extender.hasOwnProperty(key))
			extendee[key] = extender[key];
		
	return extendee;
};

//INHERITANCE/CLASS TOOLS
//Observer model
function ObserverPattern()
{
	this.subscribers = {};
}
ObserverPattern.prototype.notify = function(which)
{
	var args = Array.prototype.slice.call(arguments, 1);
	
	if(!isDef(this.subscribers[which]))
		return;
	$.each(this.subscribers[which], function(idx, how){
		how.apply(null, args);
	});
};
ObserverPattern.prototype.subscribe = function(which, how)
{
	if(!isDef(this.subscribers[which]))
		this.subscribers[which] = [];
	this.subscribers[which].push(how);
};
ObserverPattern.prototype.unsubscribe = function(which, how)
{
	if(!isDef(this.subscribers[which]))
		return;
	var where = this.subscribers[which].indexOf(how);
	if(where <= -1)
		return;
	this.subscribers[which].splice(where,1);
};

//GUIfy - Managing DOM elements and javascript controllers, (like Angular.js controllers w/o any MVC, b/c we don't do any M)
//Automatically resolves all these based on a data-guify-name = "____" where ____ is the registered name of the controller

window.GUIfy = {};
//COMMON INHERITED FUNCTIONALITY
GUIfy.objProto = {};
$.extend(GUIfy.objProto, ObserverPattern.prototype); //Requires observer pattern
//Gets the jQuery array for all GUIfy child DOM element with a given name
GUIfy.objProto.childrenEls = function(name)
{
	var foundEls = [];
	$.each(this.GUIfyChildren, function(idx,el){
		if($(el).attr("data-guify-name") === name)
			foundEls.push(el);
	});
	return $(foundEls);
};
//Gets the array of controllers in all GUIfy children with given name
GUIfy.objProto.children = function(name)
{
	if(!this.GUIfyIsReady)
		throw("Cannot perform action: Children controllers not ready");
	
	//Get all controllers of GUIfy children els
	var children = [];
	$.each(this.childrenEls(name), function(idx, el){
		children.push(el.GUIfyController);
	});
	return children;
};
//Display/hides a GUIfy object and notify
GUIfy.objProto.display = function(disp)
{
	if(!this.GUIfyIsReady)
		throw("Cannot perform action: Children controllers not ready");
	
	$.each(this.GUIfyChildren, function(idx,el){
		el.GUIfyController.display(disp);
	});
	
	//console.log("For " + this.GUIfyElement[0].tagName + "=>" + this.GUIfyElement.attr("data-guify-name") + " set " + disp);
	this.GUIfyElement.css("display", (disp ? "block" : "none"));
	this.notify("GUIfy_onDisplay", disp);
};

//A GUIfy object can be created two ways
//Automatic: DOM element names are matched up with registered controllers
//Manual: A GUIfy controller can be created on an object passing the element, the parent GUIfy element, and children GUIfy elements
//Both allow for a variable amount of arguments to be passed to the controller constructor
//In manual mode, this is as straight forward as passing the arguments like normal after the element, parent element, and child elements
//In automatic mode it's hard, default arguments can be provided to be passed to all controllers of a given kind
//Also element specific arguments can be created as an array on the element under .GUIfyController (where the controller object will end up)
//This can be done in the constructor of the GUIfy object for it's children. The elements will be present under childrenEls but the controllers
//   themselves will not be present under children yet. Once the GUIfy_onReady event is fired will they be available (see observer pattern)

//Auto mode requires the calling of GUIfyDocument(). This will solve for all children and parent elements and begin construction of all
//   valid GUIfy elements.

//GUIfyClass takes a class and makes it into a GUIfy class
//This is done by wrapping its constructor with a new class creation function (which it returns)
//and by combining the old classes members with the new class creation function's prototype
//oldCls is the old class with a constructor with 0 to vararg arguments
//elClsName is the name of the dom objects this controller will be applied to. Null will not apply it to anything (manual controller application)
//defaultArgs are the args sent as the vararg to the constructor. This can be overriden in auto mode by specifying specifically before GUIfy (see modes above)
//Example usage: function MyGUINewController(){}; MyNewGUIController = GUIfyClass(MyNewGUIController);
GUIfy.clsCallList = {};
function GUIfyClass(oldCls, elClsName, defaultArgs)
{
	//Wrap a new constructor around the old one
	var newCls = function(jEl, jParentEl, jChildrenEls) //...vararg
	{	
		//Get args to send to the constructor of new controller
		var vararg = Array.prototype.slice.call(arguments, 3);
		var appendDiff = function(pushTo, pullFrom)
		{
			for(var i=pushTo.length; i<pullFrom.length; i++)
				pushTo.push(pullFrom[i]);
		};
		
		//If missing arguments in vararg
		if(vararg.length < oldCls.length)
		{
			//Replace any missing vararg with specific args if
			if(isDef(jEl[0].GUIfyController) //Specific args exist (test 1)
				&& Object.prototype.toString.call(jEl[0].GUIfyController) === "[object Array]") //Specific args exist (test 2, make sure it's an array)
			{
				appendDiff(vararg, jEl[0].GUIfyController);
			}
			//Replace any missing vararg with default args if
			if(isDef(GUIfy.clsCallList[elClsName]["args"]) //Default args exist (test 1)
				&& GUIfy.clsCallList[elClsName]["args"].length > 0) //Length > 0 (test 2)
			{
				appendDiff(vararg, GUIfy.clsCallList[elClsName]["args"]);
			}
		}
		
		//Manually creates controller object and call constructor w/ vararg as params
		var newController = Object.create(newCls.prototype);
		ObserverPattern.apply(newController); //Super class constructor call
		newController.GUIfyElement = jEl; //Access the jQuery el from the controller
		newController.GUIfyChildren = jChildrenEls;
		newController.GUIfyParent = jParentEl;
		newController.GUIfyIsReady = false;
		oldCls.apply(newController, vararg);
		
		//Create linkage between the DOM element and the new controller
		jEl[0].GUIfyController = newController; //Access the controller from dom element
		
		return newController; //This is the new object
	};
	
	//Add all prototypes
	$.extend(newCls.prototype, GUIfy.objProto);
	$.extend(newCls.prototype, oldCls.prototype);
	
	if(isDef(elClsName))
	{
		GUIfy.clsCallList[elClsName] = {
			"cls" : newCls,
			"args" : defaultArgs
		};
	}
	
	return newCls;
}

function GUIfyDocument(jWhichEl)
{
	if(!isDef(jWhichEl))
		jWhichEl = $(document.body);
	
	//STEP 1 - Solve for all GUIfy children and parents on valid objects (with dummy object)
	var jTopGUIfyEls = GUIfyDummyElements(jWhichEl);
	
	//STEP 2 - GUIfy everything that needs it
	GUIfyChildDummiedElements(jTopGUIfyEls);
	
}
//Add dummy solver objects to all elements in a tree except root
//This adds a GUIfy_DummyFamily object to all participating elements
//It returns all topmost children in each branch
function GUIfyDummyElements(jParentEl)
{
	var GUIfyDummyChildren = [];
	var toCheck = [jParentEl];
	var localParent = isDef(jParentEl.attr("data-guify-name")) ? jParentEl : null; //No GUIfy parent if jParentEl not a GUIfy element
	while(toCheck.length > 0) //While still elements
	{
		$.each(toCheck[0].children(), function(idx, jEl){ //Check each child of toCheck
			jEl = $(jEl);
			var name = jEl.attr("data-guify-name");
			if(isDef(name) && isDef(GUIfy.clsCallList[name]))
			{
				var localChildren = GUIfyDummyElements(jEl); //Dummy all it's lower elements
				//Give it the dummy element
				jEl[0].GUIfy_DummyFamily = {
					parent : localParent,
					children : localChildren
				};
				GUIfyDummyChildren.push(jEl[0]); //Add this to current child elements
			}
			else
			{
				toCheck.push(jEl); //Otherwise, check their children
			}
		});
		toCheck.shift(); //Remove checked element
	}
	
	return $(GUIfyDummyChildren);
}
//GUIfies all elements in jParentElements and all their children using the tree built by the dummy operation
function GUIfyChildDummiedElements(jParentElements)
{
	$.each(jParentElements, function(idx, jEl){
		jEl = $(jEl);
		var name = jEl.attr("data-guify-name");
		var fam = jEl[0].GUIfy_DummyFamily;
		var newController = new GUIfy.clsCallList[name]["cls"](jEl, fam.parent, fam.children); //GUIfy this object
		if(fam.children.length > 0)
			GUIfyChildDummiedElements(fam.children); //GUIfy all children
		newController.GUIfyIsReady = true;
		newController.notify("GUIfy_onReady"); //Notify that all children are set up, can do more work
		delete jEl[0].GUIfy_DummyFamily;
	});
}
