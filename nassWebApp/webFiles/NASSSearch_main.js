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
		
		//READY 1 - Init query has finished
		var self = this;
		$.ajax("/api_init", {method : "GET"})
			.done(function(data, status, jXHR){
				self.initData = JSON.parse(data);
				self.ready();
			});
		
		//READY 2 - When DOM is ready
		$(function(){self.ready();});
	}
	NASSSearch.NASSSearchMain = NASSSearchMain;
	NASSSearchMain.prototype.ready = function()
	{
		//CHECK READYS
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
		
		//Init data on GUIfy elements
		$("#searchBuilder")[0].GUIfyController = [this];
		$("#searchResults")[0].GUIfyController = [this];
		
		//GUIfy the document
		GUIfyDocument();
		
		//Everything's ready, so grab the controllers
		this.topLevelGUIs["builderGUI"] = $("#searchBuilder")[0].GUIfyController;
		this.topLevelGUIs["resultsGUI"] = $("#searchResults")[0].GUIfyController;
		//Subscribe to all events
		this.topLevelGUIs["builderGUI"].subscribe("go", function(search){
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
				self.setGUI("resultsGUI");
			});
		});
		
		//Set the correct gui for display
		if(isDef(self.urlParams["jobid"]))
			this.setGUI("resultsGUI");
		else
			this.setGUI("builderGUI");
	};
	NASSSearchMain.prototype.setGUI = function(which)
	{
		$.each(this.topLevelGUIs, function(guiName, gui){
			gui.display(guiName == which);
		});
	};
	
})(window.NASSSearch = window.NASSSearch || {});