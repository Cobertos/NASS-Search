"use strict";

(function(NASSSearch){
	function NASSSearchMain()
	{
		//Get URLParameters
		this.urlParams = {};
		(window.onpopstate = function () {
			var match,
				search = /([^&=]+)=?([^&]*)/g,
				decode = function (s) { return decodeURIComponent(s.replace(/\+/g, " ")); },
				query  = window.location.search.substring(1);

			while (match = search.exec(query))
			   this.urlParams[decode(match[1])] = decode(match[2]);
		})();
		
		
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
		this.topLevelGUIs = {};
		this.topLevelGUIs["builderGUI"] = new NASSSearch.NASSGUI($("#searchBuilder"), NASSSearch.SearchBuilder, this);
		this.topLevelGUIs["builderGUI"].controller.subscribe("go", function(){
			//TODO: API call to perform the search
			//TODO: Get the JobID and switch guis
		});
		
		this.topLevelGUIs["resultsGUI"] = new NASSSearch.NASSGUI($("#searchResults"), NASSSearch.SearchResults, this);
		
		//Setup the guis
		var self = this;
		$.each(this.topLevelGUIs, function(guiName, gui){
			var disp = "none";
			if((guiName == "resultsGUI" && isDef(self.urlParams["jobID"]))
				|| guiName == "builderGUI")
				disp = "block";
			
			gui.jGUIEl.css({
				"display":disp
			});
		});
		
		this.isReady = true;
	};
	
})(window.NASSSearch = window.NASSSearch || {});