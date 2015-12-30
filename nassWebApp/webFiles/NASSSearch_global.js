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
GUIfy.objProto = {};
//Gets the jQuery object for a child DOM element participating in the system with a given name
GUIfy.objProto.getGUIfyChildren = function(name)
{
	var foundEl = null;
	$.each(this.GUIfyChildren, function(idx,el){
		if($(el).attr("data-guify-name") == name)
		{
			foundEl = el;
			return false;
		}
	});
	return foundEl;
};
GUIfy.objProto.GUIfyChildElements(parentEl)
{
	//Check all children for more GUIfy elements
	var GUIchildren = [];
	var toCheck = [parentEl];
	while(toCheck.length > 0) //While still elements
	{
		$.each($(toCheck[0]).children("*"), function(idx, el){ //Check each child of toCheck
			var name = $(el).attr("data-guify-name");
			if(isDef($(el).attr("data-guify-name")) && isDef(GUIfy.clsList[name]))
			{
				GUIfy.clsList[name](jEl); //GUIfy itself (will GUIfy all it's children too)
				GUIchildren.push(el); //Add to child elements
			}
			else
			{
				toCheck.push(el); //Otherwise, check their children
			}
		});
		toCheck.shift(); //Remove checked element
	}
	
	return GUIchildren;
}
//Takes a class and turns it into a GUIfy class by adding extras to it's prototype and wrapping its constructor with a new function
//oldCls should have a constructor of the form (jEl, ...)
//elClsName is the name of the dom objects this controller will be applied to. Null will not apply it to anything (manual controller application)
//Example usage: function MyGUIController(){}; MyGUIController = GUIfyClass(MyGUIController);
GUIfy.clsList = {};
function GUIfyClass(oldCls, elClsName)
{
	//Add functionality of NASSGUI object
	$.extend(oldCls.prototype, GUIfy.objProto);
	
	//Wrap around its constructor with our own
	var newCls = function(jEl) //...vararg
	{
		//Get args to send to the constructor of new controller
		var vararg = Array.prototype.slice.call(arguments, 1);
		vararg.unshift(jEl); //Add the DOM jEl to the start of the list
		
		//Manually creates controller object and call constructor w/ vararg as params
		var newController = Object.create(oldCls.prototype);
		newController = oldCls.apply(newController, vararg);
		
		//Create linkage between the DOM element and the new controller (and vice versa)
		newController.GUIfyElement = jEl; //Access the jQuery el from the controller
		jEl[0].GUIfyController = newController; //Access the controller from dom element
		
		//Find all child GUIfy elements under jEl and GUIfy them
		newController.GUIfyChildren = newController.GUIfyChildElements(jEl[0]);
		
		//Fire a function for each found child
		if(typeof newController.foundGUIfyChild === "function")
		{
			$.each(newController.GUIfyChildren, function(idx, el){
				newController.foundGUIfyChild(el);
			});
		}
	}
	
	GUIfy.clsList[elClsName] = newCls;
	
	return newCls;
}
//GUIfy an entire document, just a modified version of the GUIfy children
GUIfyDocument = GUIfy.objProto.GUIfyChildElements.apply(null, document.body);