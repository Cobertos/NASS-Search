"use strict";

//Responsible for everything related to the visual search and its control panel


(function(NASSSearch){
	function NASSSearchControl(jControlEl, jVisualEl)
	{
		//Set up the visual search portion
		this.search = new NASSSearch.NASSSearchTerm({
		"dbName" : "DB_A",
		"colName" : "Field_1",
		"searchValue" : "Value1",
		"compareFunc" : "stringEquals"});
		this.jVisualEl = jVisualEl;
		this.jSelectedEl = null;
		this.refresh();
		//Handlers
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
			
			if(jEl.is(".dbTerm"))
			{
				self.showPanel("dbTermPanel");
			}
			else if(jEl.is(".listTerm"))
			{
				self.showPanel("listTermPanel");
			}
			else if(jEl.is(".join"))
			{
				self.showPanel("joinPanel");
			}
			
			//Get all values from selectedEl and apply them to the panel
			self.getDataFromTerm(jEl[0].NASSTerm);
		});
	
		//Set up the control panels
		this.jControlPanelEls = jControlEl.children();
		this.jControlPanelEls.css("display", "none");
		this.jCurrPanelEl = null; //Start with no panel
		//Handlers
		jControlEl.on("click", "input[type='button'][name='addButton']", function(e){
			self.jSelectedEl[0].NASSTerm.add();
			self.refresh();
		});
		jControlEl.on("click", "input[type='button'][name='deleteButton']", function(e){
			self.jSelectedEl[0].NASSTerm.remove();
			self.search.prune();
			self.refresh();
		});

		jControlEl.on("change keyup", "select, input:not(input[type='button'])", function(e){
			self.applyDataToTerm(self.jSelectedEl[0].NASSTerm);
			self.refresh();
		});
	}
	NASSSearch.NASSSearchControl = NASSSearchControl;
	NASSSearchControl.prototype.showPanel = function(which)
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
	NASSSearchControl.prototype.refresh = function()
	{
		if(!isDef(this.jSelectedEl))
		{
			this.jVisualEl.html(this.search.toDOM()); //Init the entire search (doesn't matter if no selection
		}
		else
		{
			var newSelected = $(this.jSelectedEl[0].NASSTerm.toDOM());
			this.jSelectedEl.replaceWith(newSelected); //Just the selected terms contents
			this.jSelectedEl = newSelected
			this.jSelectedEl.addClass("focus");
		}
	};
	//Returns all the current panel fields as a dictionary
	NASSSearchControl.prototype.applyDataToTerm = function(term)
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to get data from";
			
		$.each(this.jCurrPanelEl.children("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			var attr = jEl.attr("name");
			var setTo = jEl.formVal();
			if(isDef(term.terms[attr])) //Only set things that actually have a value
			{
				console.log("Will apply to term dict " + attr + " | " + setTo);
				term.terms[attr] = setTo;
			}
			else if(isDef(term[attr]))
			{
				console.log("Will apply to term " + attr + " | " + setTo);
				term[attr] = setTo;
			}
		});
		this.refresh();
	};
	//USes a dictionary (data) to populate the panel
	NASSSearchControl.prototype.getDataFromTerm = function(term)
	{
		if(!isDef(this.jCurrPanelEl))
			throw "No current panel to apply data to";
			
		$.each(this.jCurrPanelEl.children("select, input").not("input[type='button']"), function(idx, jEl){
			jEl = $(jEl);
			var attr = jEl.attr("name");
			if(isDef(term.terms[attr]))
			{
				console.log("Will get from term dict " + attr);
				jEl.formVal(term.terms[attr]);
			}
			else if(isDef(term[attr]))
			{
				console.log("Will get from term " + attr);
				jEl.formVal(term[attr]);
			}
		});
	};
})(window.NASSSearch = window.NASSSearch || {});