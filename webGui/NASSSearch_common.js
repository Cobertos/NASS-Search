"use strict";

//Responsible for all the common functionality shared between a bunch of the js files

//Common functions outside namespace
function isDef(o)
{
	return !(typeof o === "undefined" || o === null);
}
//A jQuery addition to get the value of some form input
//Most return value,
//Checkbox should return true/false if checked or not
$.prototype.formVal = function(setTo)
{
	if(this.length > 1)
	{
		if(isDef(setTo))
		{
			$.each(this, function(idx,el){el.v(setTo);});
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
			var ret = this.prop("checked", setTo);
		else
			var ret = this.prop("checked");
		return ret;
	}
	else
	{
		if(isDef(setTo))
			var ret = this.val(setTo);
		else
			var ret = this.val();
		return ret;
	}
};
$.extendSelective = function(extendee, extender, filter)
{
	for(var key in extender)
		if(filter.indexOf(key) != -1 && extender.hasOwnProperty(key))
			extendee[key] = extender[key];
		
	return extendee;
};

//Observer model
function ObserverPattern()
{
	this.subscribers = {};
}
ObserverPattern.prototype.notify = function(which)
{
	var args = [];
	for(var i=1; i<arguments.length; i++)
		args[i-1] = arguments[i];
	
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

//NASSSearch related namespace stuff
//Includes the terms and joins similar to the python backend with some added functionality
(function(NASSSearch){
	function is(o, which)
	{
		switch(which)
		{
			case "func":
				return typeof o === "function";
			case "obj":
				return Object.prototype.toString.call(o) === "[object Object]";
			case "array":
				return Object.prototype.toString.call(o) === "[object Array]";
			case "string":
				return typeof o === "string";
			default:
				throw "Invalid which \"" + which + "\" specified for comparison";
		}
	}	
	
	//Holds a string (kind of like a enum)
	function NASSSearchJoin(joinName)
	{
		this.joinName = joinName;
	}
	NASSSearchJoin.prototype.toDOM = function()
	{
		var joinTerm = $.parseHTML("<div class=\"term join\">" + this.joinName + "</div>")[0];
		joinTerm.NASSTerm = this;
		return joinTerm;
	};
	NASSSearchJoin.prototype.toJSON = function()
	{
		return this.joinName;
	};

	//Holds an entire search similar to the python version
	function NASSSearchTerm(terms, noErrorCheck)
	{
		this.inverse = false;
		this.terms = terms;
		if(!(isDef(noErrorCheck) && noErrorCheck))
			this.errorCheck();
		
		this.flagDelete = false;
	};
	NASSSearch.NASSSearchTerm = NASSSearchTerm;
	NASSSearchTerm.prototype.errorCheck = function(){
		//Safety check for empty lists
		if(this.terms.length == 0)
			throw "No search terms were given"
		//Error check a dictionary (or in javascript, a plain object as an assoc array) (db Term)
		if(is(this.terms, "obj"))
		{
			var keys = Object.keys(this.terms);
			if(keys.length != 4 || !($.inArray("dbName", keys) > -1) || !($.inArray("colName", keys) > -1) || !($.inArray("searchValue", keys) > -1) || !($.inArray("compareFunc", keys) > -1))
				throw "Dictionary for search term did not contain the right terms";
		}
		//Error check an array (list term)
		else if(is(this.terms, "array"))
		{
			if(this.terms.length == 1)
				throw "Only one search term given. Do not create list terms containing one term.";
			if(this.terms.length % 2 != 1)
				throw "Search must contain an odd number of terms";
				
			$.each(this.terms, function(idx, term){
				//Even Term
				if(idx % 2 == 0 && !(term instanceof NASSSearchTerm))
					throw "Even term was not a search term";
				//Odd Term
				else if(idx % 2 == 1 && !(term instanceof NASSSearchJoin))
					throw "Odd term was not a join term";
				//Recursive check
				if(term instanceof NASSSearchTerm)
					term.errorCheck();
			});
		}
		else
		{
			throw "Terms was not a dict term or a list term";
		}
	};
	//Remove any terms from the entire tree that are flagDelete (from .remove)
	//condense by default is true, condenses a listTerm with one term into a dictTerm
	NASSSearchTerm.prototype.prune = function(condense, onlyFirstLevel)
	{
		if(!isDef(condense))
			condense = true;
		if(!isDef(onlyFirstLevel))
			onlyFirstLevel = false;
		
		if(is(this.terms, "obj"))
			return; //Nothing we can do about ourselves
		else if(is(this.terms, "array"))
		{
			var self = this;
			$.each(this.terms, function(idx, term){
				if(term instanceof NASSSearchTerm && term.flagDelete)
				{
					if(idx == self.terms.length-1)
					{
						//Last term, must remove the join before, not after
						self.terms.splice(idx-1,2);
					}
					else
					{
						//Remove the term and following join
						self.terms.splice(idx, 2);
					}
					return false; //Should only delete once per prune of an listTerm (for now)
				}
				else if(term instanceof NASSSearchTerm)
				{
					if(!onlyFirstLevel)
						this.prune(condense, onlyFirstLevel);
					else
						this.prune(); //Prune with defaults
				}
			});
		}
		if(condense && this.terms.length == 1)
		{
			//If there's only one element left, make this object a dict object
			this.terms = this.terms[0].terms;
		}
	};
	//Remove a term
	NASSSearchTerm.prototype.remove = function()
	{
		this.flagDelete = true;
	};
	//Add an empty term
	NASSSearchTerm.prototype.add = function(addTerm)
	{
		//Make a new parenthesis term containing this term
		if(is(this.terms, "obj")) 
			this.terms = [new NASSSearchTerm(this.terms), new NASSSearchJoin("AND"), addTerm];
		//Otherwise just add a term + join (if needed)
		else if(is(this.terms, "array"))
		{
			if(this.terms.length == 0)
				this.terms.push(addTerm);
			else
			{
				this.terms.push(new NASSSearchJoin("AND"));
				this.terms.push(addTerm);
			}
		}
	};
	//Generates a DOM tree of the search with lots of different classes for styling
	//Also, every term in the tree has a NASSTerm tag on it to get the term it represents in the class tree
	NASSSearchTerm.prototype.toDOM = function()
	{	
		//Create the outer most div of the term with all classes
		var topTerm = $.parseHTML("<div class=\"term"
		+ (this.inverse ? " not" : "")
		+ (is(this.terms, "obj") ? " dbTerm" : " listTerm")
		+ "\"></div>")[0];
		topTerm.NASSTerm = this; //Save ourselves on the DOM node for future reference
		
		var uprLeftTerm = $.parseHTML("<div class=\"uprLeft\"></div>")[0];
		var uprLeftText = (this.inverse ? "Not" : "");
		
		//Convert the term to DOM
		var nodes;
		if(is(this.terms, "obj"))
		{
			//A dict term is just some text nodes
			uprLeftText += (uprLeftText.length > 0 ? " | " : "") + this.terms["dbName"];
			nodes = [document.createTextNode(this.terms["colName"] + " == " + this.terms["searchValue"])];
		}
		else if(is(this.terms, "array"))
		{
			//A list term is more terms and join terms
			nodes = []
			$.each(this.terms, function(idx, term){
				nodes.push(term.toDOM());
			});
		}
		//Put them all in the outer term
		$.each(nodes, function(idx, node){
			topTerm.appendChild(node);
		});
		
		//Prepend any upper left text if necessary
		if(uprLeftText.length > 0)
		{
			uprLeftTerm.appendChild(document.createTextNode(uprLeftText));
			topTerm.insertBefore(uprLeftTerm, topTerm.firstChild);
		}
		
		return topTerm;
	};
	NASSSearchTerm.prototype.toJSON = function()
	{
		throw "Not implemented yet";
	};
})(window.NASSSearch = window.NASSSearch || {});