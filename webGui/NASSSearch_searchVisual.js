"use strict";

//Responsible for everything related to the visual search and its control panel


(function(NASSSearch){
	//The visual search panel
	function NASSSearchVisual(searchInit, jVisualEl)
	{
		//A small wrapper around the full search for UI purposes
		//Becomes a term with one term in it, this term will eventually be stripped off when finalizing the search
		this.search = new NASSSearch.NASSSearchTerm([], true);
		if(isDef(searchInit))
			this.search.terms.push(searchInit);
		
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
		
		this.jVisualEl = jVisualEl;
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
			
			var which = "";
			if(jEl.is(".rootTerm"))
				which = "rootTerm";
			else if(jEl.is(".dbTerm"))
				which = "dbTerm";
			else if(jEl.is(".listTerm"))
				which = "listTerm";
			else if(jEl.is(".join"))
				which = "join";
			
			//Notify of selection, what type, and the term
			self.notify("select", which, jEl[0].NASSTerm);
		});
		
		this.refresh();
	}
	NASSSearch.NASSSearchVisual = NASSSearchVisual;
	NASSSearchVisual.prototype = $.extend({}, new ObserverPattern());
	NASSSearchVisual.prototype.refresh = function()
	{
		if(!isDef(this.jSelectedEl))
		{
			this.jVisualEl.html(this.search.toDOM()); //Init the entire search (doesn't matter if no selection
		}
		else
		{
			var newSelected = $(this.jSelectedEl[0].NASSTerm.toDOM(false));
			this.jSelectedEl.replaceWith(newSelected); //Just the selected terms contents (so we can reapply the focus)
			this.jSelectedEl = newSelected
			this.jSelectedEl.addClass("focus");
		}
	};
	NASSSearchVisual.prototype.applyDataToSelected = function(data)
	{
		//Data is a dictionary of term attributes (in the dict term or on the term itself) to values
		var term = this.jSelectedEl[0].NASSTerm;
		$.each(data, function(k, v){
			if(isDef(term.terms[k])) //Only set things that actually have a value
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
	NASSSearchVisual.prototype.addSelected = function()
	{
		var blankTerm = new NASSSearch.NASSSearchTerm(
		{"dbName":"Empty",
		"colName":"Empty",
		"searchValue":"Empty",
		"compareFunc":"Empty"});
		
		this.jSelectedEl[0].NASSTerm.add(blankTerm);
		this.refresh();
	};
	NASSSearchVisual.prototype.removeSelected = function()
	{
		this.jSelectedEl[0].NASSTerm.remove();
		this.search.prune();
		this.refresh();
	}
	
	//The control panel that ties in with the visual search panel
	function NASSSearchPanel(jControlEl)
	{
		//Set up the control panels
		this.jControlPanelEls = jControlEl.children();
		this.jControlPanelEls.css("display", "none");
		this.jCurrPanelEl = null; //Start with no panel
		//Handlers
		var self = this;
		jControlEl.on("click", "input[type='button'][name='addButton']", function(e){
			self.notify("add");
		});
		jControlEl.on("click", "input[type='button'][name='deleteButton']", function(e){
			self.notify("delete");
		});
		jControlEl.on("change keyup", "select, input:not(input[type='button'])", function(e){
			self.notify("change");
		});
	}
	NASSSearch.NASSSearchPanel = NASSSearchPanel;
	NASSSearchPanel.prototype = $.extend({}, new ObserverPattern());
	NASSSearchPanel.prototype.showPanel = function(which)
	{
		if(isDef(which))
		{
			var foundPanel = this.jControlPanelEls.filter("." + which);
			if(foundPanel.length <= 0)
				throw "Control panel " + which + " not found";
			this.jCurrPanelEl = foundPanel;
			this.jControlPanelEls.css("display", "none");
			this.jCurrPanelEl.css("display", "block");
			
			//Should populate the panel with appropriate data
		}
		else
		{
			this.jControlPanelEls.css("display", "none");
			this.jCurrPanelEl = null;
		}
	};
	NASSSearchPanel.prototype.getDataFromPanel = function()
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to get data from";
		
		var ret = {};
		$.each(this.jCurrPanelEl.children("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			ret[jEl.attr("name")] = jEl.formVal();
		});
		return ret;
	};
	NASSSearchPanel.prototype.applyTermToPanel = function(term)
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to apply data to";
			
		$.each(this.jCurrPanelEl.children("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			var attr = jEl.attr("name");
			if(isDef(term.terms[attr]))
			{
				jEl.formVal(term.terms[attr]);
			}
			else if(isDef(term[attr]))
			{
				jEl.formVal(term[attr]);
			}
		});
	};
	
	//Responsible for the observation of the entire application
	function NASSSearchControl(jControlEl, jVisualEl)
	{
		//Set up the visual search portion
		this.searchBuilderVisual = new NASSSearchVisual(null, jVisualEl);
		this.searchBuilderPanel = new NASSSearchPanel(jControlEl);
		
		//All the connections
		var self = this;
		this.searchBuilderVisual.subscribe("select", function(which, term){
			self.searchBuilderPanel.showPanel(which + "Panel");
			self.searchBuilderPanel.applyTermToPanel(term);
		});
		this.searchBuilderPanel.subscribe("add", function(){
			self.searchBuilderVisual.addSelected();
		});
		this.searchBuilderPanel.subscribe("delete", function(){
			self.searchBuilderVisual.removeSelected();
		});
		this.searchBuilderPanel.subscribe("change", function(){
			var data = self.searchBuilderPanel.getDataFromPanel();
			self.searchBuilderVisual.applyDataToSelected(data);
		});
	}
	NASSSearch.NASSSearchControl = NASSSearchControl;
})(window.NASSSearch = window.NASSSearch || {});