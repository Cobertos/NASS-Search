"use strict";

(function(NASSSearch){
	function NASSSearchMain()
	{
		//Get URLParameters
		this.urlParams = {};
		
		//Variables for handling when to init
		this.isReady = false;
		this.readys = 0;
		this.readysNeeded = 2;
		
		//Everything else
		this.initData = null;
		this.builderGUI = null;
		this.resultsGUI = null;
		
		//Perform the init query
		var self = this;
		$.ajax("/api_init", {method : "GET"})
			.done(function(data, status, jXHR){
				self.initData = JSON.parse(data);
				self.ready();
			});
		
		$(function(){self.ready();});
	}
	NASSSearch.NASSSearchMain = NASSSearchMain;
	NASSSearchMain.prototype.ready = function()
	{
		this.readys += 1;
		if(this.readys < this.readysNeeded)
			return;
		//FULLY READY
		//Get Url parameters
		var match,
			search = /([^&=]+)=?([^&]*)/g,
			decode = function (s) { return decodeURIComponent(s.replace(/\+/g, " ")); },
			query  = window.location.search.substring(1);

		while (match = search.exec(query))
		   this.urlParams[decode(match[1])] = decode(match[2]);
		
		//Create all the sub gui systems
		var self = this;
		this.topLevelGUIs = {};
		this.topLevelGUIs["builderGUI"] = new NASSSearch.NASSGUI($("#searchBuilder"), NASSSearch.SearchBuilder, this);
		this.topLevelGUIs["builderGUI"].controller.subscribe("go", function(search){
			self.initData["search"] = search;
			$.ajax("/api_search", {
				contentType : "application/json; charset=UTF-8",
				method : "POST",
				data : JSON.stringify(search),
				processData : false
			})
			.done(function(data, status, jXHR){
				var json = JSON.parse(data);
				console.log(json);
				self.urlParams["jobid"] = json["jobid"];
				self.setGUI();
			});
		});
		
		this.topLevelGUIs["resultsGUI"] = new NASSSearch.NASSGUI($("#searchResults"), NASSSearch.SearchResults, this);
		
		this.isReady = true;
		
		this.setGUI();
	};
	NASSSearchMain.prototype.setGUI = function(which)
	{
		var self = this;
		$.each(this.topLevelGUIs, function(guiName, gui){
			var disp = "none";
			if((guiName == "resultsGUI" && isDef(self.urlParams["jobid"]))
				|| guiName == "builderGUI" && !isDef(self.urlParams["jobid"]))
				disp = "block";
			
			gui.jGUIEl.css({
				"display":disp
			});
			
			if(isDef(gui.controller.init) && disp == "block")
				gui.controller.init();
		});
	};
	
})(window.NASSSearch = window.NASSSearch || {});