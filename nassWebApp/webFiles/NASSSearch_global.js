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
			$.each(this, function(idx,el){el.formVal(setTo);});
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

GUIfy = {};
//COMMON INHERITED FUNCTIONALITY
GUIfy.objProto = {};
$.extend(GUIfy.objProto, new ObserverPattern()); //Requires observer pattern
//Gets the jQuery array for all GUIfy child DOM element with a given name
GUIfy.objProto.childrenEls = function(name)
{
	var foundEls = [];
	$.each(this.GUIfyChildren, function(idx,jEl){
		jEl = $(jEl);
		if(jEl.attr("data-guify-name") === name)
			foundEls.push(jEl);
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
	
	this.GUIfyElement.css("display", (disp ? "block" : "none"));
	this.notify("GUIfy_onDisplay", disp);
	$.each(this.GUIfyChildren, function(idx,el){
		el.GUIfyController.notify("GUIfy_onDisplay");
	});
};

//A GUIfy object can be created two ways
//Automatic: 

//First solve the tree for GUIfy objects, get all children parents
//Then solve the tree for GUIfy
//Constructor - 


//Auto: The name is matched up with the registered name of a controller. It is given default arguments except those substituted by specific functions before ready
//Manual: The element is passed to the constructor of the controller and is given arguments there. Ready is called right after the constructor with those args
//In both cases, ready is the constructor. It helps because in the auto mode, we can be assured all children have been created and also that all args are set for creation


//Takes a class and turns it into a GUIfy class by adding extras to it's prototype and wrapping its constructor with a new function
//oldCls should have a constructor of the form (jEl, ...) where ... is any variable amount of arguments
//elClsName is the name of the dom objects this controller will be applied to. Null will not apply it to anything (manual controller application)
//defaultArgs are the args sent as the vararg to the constructor. This can be overriden in auto mode by specifying specifically before GUIfy OR 
//Example usage: function MyGUINewController(){}; MyNewGUIController = GUIfyClass(MyNewGUIController);
GUIfy.clsCallList = {};
function GUIfyClass(oldCls, elClsName, defaultArgs)
{
	//Add functionality of GUIfy object
	$.extend(oldCls.prototype, GUIfy.objProto);
	
	//Wrap around its constructor with our own
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
				&& Object.prototype.toString.call(o) === "[object Array]") //Specific args exist (test 2, make sure it's an array)
			{
				appendDiff(vararg, jEl[0].GUIfyController);
			}
			//Replace any missing vararg with default args if
			if(isDef(GUIfy.clsList[elClsName]) //Default args exist (test 1)
				&& GUIfy.clsList[elClsName].length > 0) //Length > 0 (test 2)
			{
				appendDiff(vararg, GUIfy.clsList[elClsName]);
			}
		}
		
		//Manually creates controller object and call constructor w/ vararg as params
		var newController = Object.create(oldCls.prototype);
		newController.GUIfyElement = jEl; //Access the jQuery el from the controller
		newController.GUIfyChildren = jChildrenEls;
		newController.GUIfyParent = jParentEl;
		newController = oldCls.apply(newController, vararg);
		
		newController.GUIfyIsReady = false;
		newController.subscribe("GUIfy_onReady", function onReady(){
			newController.GUIfyIsReady = true;
			newController.unsubscribe("GUIfy_onReady", onReady);
		});
		
		//Create linkage between the DOM element and the new controller
		jEl[0].GUIfyController = newController; //Access the controller from dom element
	}
	
	GUIfy.clsList[elClsName] = {
		"cls" : newCls,
		"args" : defaultArgs
	};
	
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
			if(isDef(name) && isDef(GUIfy.clsList[name]))
			{
				var localChildren = GUIfyDummyElements(jEl); //Dummy all it's lower elements
				//Give it the dummy element
				jEl[0].GUIfy_DummyFamily = {
					parent : localParent,
					children : localChildren
				};
				GUIfyDummyChildren.push(jEl); //Add this to current child elements
			}
			else
			{
				toCheck.push(el); //Otherwise, check their children
			}
		});
		toCheck.shift(); //Remove checked element
	}
	
	return $(GUIfyDummyChildren);
}
//GUIfies all elements in jParentElements and all their children using the tree built by the dummy operation
function GUIfyChildDummiedElements(jParentElements)
{
	var name = jEl.attr("data-guify-name");
	$.each(jParentElements, function(){
		var fam = jEl[0].GUIfy_DummyFamily;
		var newObj = GUIfy.clsList[name](jEl, fam.parent, fam.children); //GUIfy this object
		GUIfyChildDummiedElements(fam.children); //GUIfy all children
		newObj.notify("GUIfy_onReady"); //Notify that all children are set up, can do more work
	});
}
