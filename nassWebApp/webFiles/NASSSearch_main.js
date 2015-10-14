"use strict";

(function(NASSSearch){
	function NASSSearchMain()
	{
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
		
		//Create all the sub gui systems
		var controller;
		this.builderGUI = new NASSSearch.NASSGUI($("#searchBuilder"), NASSSearch.SearchBuilder, this);
		this.builderGUI.controller.subscribe("go", function(){
			//TODO: API call to perform the search
			//TODO: Get the JobID and switch guis
		});
		
		//this.resultsGUI = new NASSSearch.NASSGUI($("#searchResults"), NASSSearch.SearchResults, this);
		
		
		this.isReady = true;
	};
	
})(window.NASSSearch = window.NASSSearch || {});