"use strict";

(function(NASSSearch){
	function NASSSearchMain()
	{
		this.isReady = false;
		this.readys = 0;
		this.readysNeeded = 2;
		
		this.initData = null;
		this.searchGUI = null;
		
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
		
		this.searchGUI = new NASSSearch.NASSSearchControl(this, $("#searchControl"), $("#searchVisual"));
		
		this.isReady = true;
	};
	
})(window.NASSSearch = window.NASSSearch || {});