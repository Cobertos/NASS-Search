"use strict";

//Responsible for everything related to the visual search and its control panel


(function(NASSSearch){
	//The visual search panel
	function SearchBuilderVisual(thisGUI, searchInit, blankTerm)
	{
		//A small wrapper around the full search for UI purposes
		//Becomes a term with one term in it, this term will eventually be stripped off when finalizing the search
		this.search = new NASSSearch.NASSSearchTerm([], true);
		if(isDef(searchInit))
			this.search.terms.push(searchInit);
		//Patch the rootTerm's toJSON to get JSON without the rootTerm
		var oldToJSON = this.search.toJSON;
		this.search.toJSON = function()
		{
			if(this.terms.length == 0)
				return "";
			else
				return oldToJSON.call(this);
		}
		
		//Patch the rootTerm's toDOM to give it special classes
		var oldToDOM = this.search.toDOM;
		this.search.toDOM = function()
		{
			var dom = oldToDOM.call(this);
			var jThisEl = $(dom);
			jThisEl.addClass("rootTerm");
			if(this.terms.length == 0)
				jThisEl.addClass("emptyListTerm");
			
			return jThisEl[0];
		}
		
		this.blankTerm = blankTerm;
		
		this.jVisualEl = thisGUI.jGUIEl;
		this.jSelectedEl = null;

		//Set up all the handlers
		var self = this;
		this.jVisualEl.on("mouseover", ".term", function(e){
			e.stopPropagation();
			$(e.target).addClass("hover");
		});
		this.jVisualEl.on("mouseout", ".term", function(e){
			e.stopPropagation();
			$(e.target).removeClass("hover");
		});
		this.jVisualEl.on("click", ".term", function(e){
			e.stopPropagation();
			var jEl = $(e.target);
			
			if(isDef(self.jSelectedEl))
			{
				self.jSelectedEl.removeClass("focus");
			}
			self.jSelectedEl = jEl;
			jEl.addClass("focus");
			
			//Notify of selection, what type, and the term
			self.notify("select", self.getTermType(jEl), jEl[0].NASSTerm);
		});
		
		this.refresh();
	}
	NASSSearch.SearchBuilderVisual = SearchBuilderVisual;
	SearchBuilderVisual.prototype = $.extend({}, new ObserverPattern());
	SearchBuilderVisual.prototype.getTermType = function(jTermEl)
	{
		if(jTermEl.is(".rootTerm"))
			return "rootTerm";
		else if(jTermEl.is(".dbTerm"))
			return "dbTerm";
		else if(jTermEl.is(".listTerm"))
			return "listTerm";
		else if(jTermEl.is(".join"))
			return "join";
		else
			throw "Unidentified term";
	};
	SearchBuilderVisual.prototype.refresh = function()
	{	
		if(!isDef(this.jSelectedEl))
		{
			this.jVisualEl.html(this.search.toDOM()); //Init the entire search (doesn't matter if no selection
		}
		else
		{
			//Test for a term change in the DOM
			var oldTermType = this.getTermType(this.jSelectedEl);
			
			var newSelected = $(this.jSelectedEl[0].NASSTerm.toDOM(false));
			this.jSelectedEl.replaceWith(newSelected); //Just the selected terms contents (so we can reapply the focus)
			this.jSelectedEl = newSelected;
			this.jSelectedEl.addClass("focus");
			
			//Did it change term type? Fire a new selection
			if(oldTermType != this.getTermType(this.jSelectedEl))
				this.notify("select", this.getTermType(this.jSelectedEl), this.jSelectedEl[0].NASSTerm);
		}
	};
	SearchBuilderVisual.prototype.applyDataToSelected = function(data)
	{
		//Data is a dictionary of term attributes (in the dict term or on the term itself) to values
		var term = this.jSelectedEl[0].NASSTerm;
		$.each(data, function(k, v){
			if(isDef(term.terms) && isDef(term.terms[k])) //Only set things that actually have a value
			{
				term.terms[k] = v;
			}
			else if(isDef(term[k]))
			{
				term[k] = v;
			}
		});
		this.refresh();
	};
	SearchBuilderVisual.prototype.addSelected = function()
	{
		this.jSelectedEl[0].NASSTerm.add(this.blankTerm.copy());
		this.refresh();
	};
	SearchBuilderVisual.prototype.removeSelected = function()
	{
		this.jSelectedEl[0].NASSTerm.remove();
		this.search.prune(false, true); //Only condense things above the first level in this.search
		this.jSelectedEl = null;
		this.refresh();
	}
	
	//The control panel that ties in with the visual search panel
	function SearchBuilderControl(thisGUI, supportedData)
	{
		//Set up the control panels
		var jControlEl = thisGUI.jGUIEl;
		this.jControlPanelEls = jControlEl.children();
		this.jControlPanelEls.css("display", "none");
		this.jCurrPanelEl = null; //Start with no panel
		this.supportedData = supportedData;
		
		//Handlers
		var self = this;
		jControlEl.on("click", "input[type='button'][name='addButton']", function(e){
			self.notify("add");
		});
		jControlEl.on("click", "input[type='button'][name='deleteButton']", function(e){
			self.notify("delete");
		});
		jControlEl.on("change keyup", "select, input:not(input[type='button'])", function(e){
			//Update the menus
			self.fillPanel(false);
			self.notify("change");
		});
	}
	NASSSearch.SearchBuilderControl = SearchBuilderControl;
	SearchBuilderControl.prototype = $.extend({}, new ObserverPattern());
	SearchBuilderControl.prototype.showPanel = function(which)
	{
		
		if(!isDef(which))
		{
			this.jControlPanelEls.css("display", "none");
			this.jCurrPanelEl = null;
			return;
		}
		
		var foundPanel = this.jControlPanelEls.filter("." + which);
		if(foundPanel.length <= 0)
			throw "Control panel " + which + " not found";
		this.jCurrPanelEl = foundPanel;
		this.jControlPanelEls.css("display", "none");
		this.jCurrPanelEl.css("display", "block");
		
		this.fillPanel(true);
	};
	//Fill all data inputs
	//fullFill - Fill all inputs or just update dependant ones?
	SearchBuilderControl.prototype.fillPanel = function(fullFill)
	{
		//Fill all the select tags
		var fillSelect = function(jSelectEl, strArray)
		{
			var options = "";
			var selected = false;
			$.each(strArray, function(idx, str){
				options += "<option" + (selected ? "" : " selected=\"selected\"" ) + " value=\"" + str + "\">" + str + "</option>";
				selected = true;
			});
			jSelectEl.html(options);
		};
		
		var self = this;
		var toFill = this.jCurrPanelEl.find("select");
		var filled = {};
		while(toFill.length > 0)
		{
			//Fill all the select tags
			$.each(toFill.slice(), function(idx, jEl){
				jEl = $(jEl);
				var name = jEl.attr("name");
				var fillData = self.supportedData[name];
				if(!isDef(fillData))
					throw "No fill data for select";
				
				//Fill Data is Array => Use array to fill select array
				if(Object.prototype.toString.call(fillData) === "[object Array]")
				{
					if(fullFill)
					{
						fillSelect(jEl, fillData.sort());
					}
					//else - Skip it
				}
				//Fill Data is Object (dictionary) => Use key value of some other select to get the array to populate with
				else if(Object.prototype.toString.call(fillData) === "[object Object]")
				{
					//Get the key to use as the index for the object with fill data arrays
					var fillKey = null;
					//Relies on another select tag
					if(name == "colName" && isDef(filled["dbName"]))
						fillKey = filled["dbName"].val();
					else
						throw "Dependant select not informed of other select.";
					
					//If fullFill (always fill) or if the current fillKey differs from the one it was filled with, fill it
					if(fullFill || (isDef(jEl[0].fillKey) && jEl[0].fillKey != fillKey))
					{
						fillSelect(jEl, fillData[fillKey].sort());
						jEl[0].fillKey = fillKey;
					}
					//else - Skip it
				}
				else
				{
					throw "Unexpected type for select object";
				}
				
				//Mark as filled and record for dependancies
				filled[name] = jEl;
				toFill = toFill.not(jEl);
			});
		}
	};
	SearchBuilderControl.prototype.getDataFromPanel = function()
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to get data from";
		
		var ret = {};
		$.each(this.jCurrPanelEl.find("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			ret[jEl.attr("name")] = jEl.formVal();
		});
		return ret;
	};
	SearchBuilderControl.prototype.applyTermToPanel = function(term)
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to apply data to";
		
		$.each(this.jCurrPanelEl.find("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			var attr = jEl.attr("name");
			if(isDef(term.terms) && isDef(term.terms[attr]))
			{
				jEl.formVal(term.terms[attr]);
			}
			else if(isDef(term[attr]))
			{
				jEl.formVal(term[attr]);
			}
		});
		
		this.fillPanel(false);
		this.notify("change");
	};
	
	//The panel that controls all other misc options
	function SearchMiscControl(thisGUI, supportedData)
	{
		//This is a simple module
		//It fills selects with default data and otherwise just packages up all data by name
		//It also looks for the go button
	}
	NASSSearch.SearchMiscControl = SearchMiscControl;
	SearchMiscControl.prototype = $.extend({}, new ObserverPattern());
	
	//The panel that has the go button and alerts
	function SearchGoControl(thisGUI)
	{
		//A simple module that notifies on button push
		//Also responsible for setting the alerts next to the button
	}
	NASSSearch.SearchGoControl = SearchGoControl;
	SearchGoControl.prototype = $.extend({}, new ObserverPattern());
	
	
	//Responsible for the observation of the entire application
	function SearchBuilder(thisGUI, nassMain)
	{
		//Set up the different guis
		var blankTerm = new NASSSearch.NASSSearchTerm(
		{"dbName":nassMain.initData["dbName"][0],
		"colName":nassMain.initData["colName"][nassMain.initData["dbName"][0]][0],
		"searchValue":"Value",
		"compareFunc":nassMain.initData["compareFunc"][0]});
		var jEl;
		//Visual GUI
		jEl = thisGUI.getChild("builderVisual");
		this.searchBuilderVisualGUI = new NASSSearch.NASSGUI(jEl, SearchBuilderVisual, null, blankTerm);
		var searchBuilderVisual = this.searchBuilderVisualGUI.controller;
		//Control GUI
		jEl = thisGUI.getChild("builderControl");
		this.searchBuilderControlGUI = new NASSSearch.NASSGUI(jEl, SearchBuilderControl, nassMain.initData);
		var searchBuilderControl = this.searchBuilderControlGUI.controller;
		//Misc GUI
		jEl = thisGUI.getChild("misc");
		this.miscControlGUI = new NASSSearch.NASSGUI(jEl, SearchMiscControl, nassMain.initData);
		var miscControl = this.miscControlGUI.controller;
		//Go Panel GUI
		jEl = thisGUI.getChild("go");
		this.goControlGUI = new NASSSearch.NASSGUI(jEl, SearchGoControl);
		var goControl = this.goControlGUI.controller;
		
		//All the connections
		var self = this;
		searchBuilderVisual.subscribe("select", function(which, term){
			searchBuilderControl.showPanel(which + "Panel");
			searchBuilderControl.applyTermToPanel(term);
		});
		searchBuilderControl.subscribe("add", function(){
			searchBuilderVisual.addSelected();
		});
		searchBuilderControl.subscribe("delete", function(){
			searchBuilderVisual.removeSelected();
		});
		searchBuilderControl.subscribe("change", function(){
			var data = searchBuilderControl.getDataFromPanel();
			searchBuilderVisual.applyDataToSelected(data);
			//self.doPresearch();
		});
		miscControl.subscribe("change", function(){
			//self.doPresearch();
		});
		goControl.subscribe("go", function(){
			this.notify("go"); //Propogate the message
		});
	}
	NASSSearch.SearchBuilder = SearchBuilder;
	SearchBuilder.prototype = $.extend({}, new ObserverPattern());
	/*SearchBuilder.prototype.doPresearch = function(fromTimeout)
	{
		//Clear the timeout
		if(isDef(this.presearchTimeout))
			window.clearTimeout(this.presearchTimeout);
		
		//Timeout expired, not a user causing presearch again, react to the data
		if(fromTimeout === true)
		{
			$.ajax("/api_presearch", {method : "GET"})
			.done(function(data, status, jXHR){
				console.log(data);
				//self.goControl.applyAlerts(JSON.parse(data));
			});
		}
		else //Wait another 300ms until timer expires
		{
			var func = this.doPresearch.bind(this, true);
			this.presearchTimeout = window.setTimeout(func, 300); //300ms
		}
	};*/
})(window.NASSSearch = window.NASSSearch || {});