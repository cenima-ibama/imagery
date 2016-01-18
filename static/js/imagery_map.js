'use strict';

var seeOnMap;

$(document).ready(function() {
	var lastBbox,
		el = $('#formBounds'),
		bbox = $('#bbox').attr('value'),
		pageInfo = $('#page_number').attr('value');

	var drawnItems = new L.FeatureGroup();

	var drawControl = new L.Control.Draw({
		position: 'topright',
		edit: {
			featureGroup: drawnItems,
			remove: false,
			edit: false,
		},
		draw: {
			polyline: false,
			polygon: false,
			circle: false,
			marker: false,
			rectangle: {
				shapeOptions: {
					color: 'black',
					weight: 3
				}
			},
		},
	});

	var drawControlEditOnly = new L.Control.Draw({
		position: 'topright',
		draw: false,
		edit: {
			featureGroup: drawnItems
		},
	});

	imageryMap.addLayer(drawnItems);
	imageryMap.addControl(drawControl);

	imageryMap.on('draw:created', drawCreated);
	imageryMap.on('draw:edited', drawEdited);
	imageryMap.on("draw:deleted", drawDeleted);
	imageryMap.on('draw:drawstart', function(e){ startDrawing( $('#search') ) } );
	imageryMap.on('draw:editstart', function(e){ startDrawing( $('#search') ) });
	imageryMap.on('draw:deletestart', function(e){ startDrawing( $('#search') ) });

	imageryMap.on('draw:drawstop', function(e){ stopDrawing( $('#search') ) });
	imageryMap.on('draw:deletestop', function(e){ stopDrawing( $('#search') ) });
	imageryMap.on('draw:editstop', function(e){ stopDrawing( $('#search') ) });

	function drawCreated(e){
		var type = e.layerType,
		layer = e.layer;
		drawnItems.addLayer(layer);

		manageControl(drawControlEditOnly, drawControl);

		bbox = layer.getBounds();
		var northEast = bbox.getNorthEast();
		var southWest = bbox.getSouthWest();
		bbox = northEast.lng + ',' + northEast.lat + ',' + southWest.lng + ',' + southWest.lat;

		lastBbox = bbox;

		defineLatLngBounds(lastBbox);
		stopDrawing($("#search"));
		ShowHide('.edit-group', '.draw-group');
		editDrawControl();
	}


	function drawEdited(e){
		var layers = e.layers;

		layers.eachLayer(function (layer) {
			bbox = layer.getBounds();
			var northEast = bbox.getNorthEast();
			var southWest = bbox.getSouthWest();
			bbox = northEast.lng + ',' + northEast.lat + ',' + southWest.lng + ',' + southWest.lat;
		});

		lastBbox = bbox;
		defineLatLngBounds(lastBbox);
		stopDrawing($("#search"));
	}


	function drawDeleted(e){
		var i=0;

		$.each(drawnItems._layers, function(value, key){
			if(value && key)
				i++;
		});

		if(!i){
			if(drawControlEditOnly._map){
				manageControl(drawControl, drawControlEditOnly);
				lastBbox = false;
			}
			defineLatLngBounds(lastBbox);
			ShowHide('.draw-group', '.edit-group');
			stopDrawing($("#search"));
			editDrawControl();
		}

	}


	function getRectangle(data){
		data = data.split(',').map(function(a){ return parseFloat(a); });
		/* reverting data to return lat lng to application */
		data = [[data[1], data[0]],[data[3], data[2]]];

		var layer = L.rectangle(data, {color: "green", weight: 3});
		return drawnItems.addLayer(layer);
	}


	function startDrawing(el){
		el.attr('disabled','disabled');
	}


	function stopDrawing(el){
		el.removeAttr('disabled');
	}


	function defineLatLngBounds(lastBbox){
		var el = $('#formBounds');
		lastBbox ? el.attr('value', lastBbox) : el.removeAttr('value');
	}


	function manageControl(newControl, oldControl){
		oldControl.removeFrom(imageryMap);
		newControl.addTo(imageryMap);
	}


	function ShowHide(show, hide){
		$(hide).hide();
		$(show).show();
	}


	function editDrawControl(){
		$('.leaflet-draw-toolbar').addClass('edit-control');

		$('.leaflet-draw-draw-rectangle').addClass('btn-draw');
		$('.leaflet-draw-edit-edit').addClass('btn-edit');
		$('.leaflet-draw-edit-remove').addClass('btn-remove');

		$('.edit-control').removeClass('leaflet-draw-toolbar ');
		$('.btn-edit').removeClass('leaflet-draw-edit-edit');
		$('.btn-remove').removeClass('leaflet-draw-edit-remove');
		$('.btn-draw').removeClass('leaflet-draw-draw-rectangle');

		$('.btn-draw').append('Draw Area');
		$('.btn-edit').append('Edit');
		$('.btn-remove').append('Delete');

	}

	seeOnMap = function(id){
		id = $(id).attr('id');

		if(lastSelectedLayer)
			lastSelectedLayer.setStyle({
				color: '#03f',
				weight: 1,
				fillColor: '#03f',
			});

		if(geoJsonLayer.hasOwnProperty(id) && geoJsonLayer[id]){
			lastSelectedLayer = geoJsonLayer[id];
			geoJsonLayer[id].setStyle({
				color: 'red',
				weight: 3,
				fillColor: 'red',
			});
			imageryMap.fitBounds(geoJsonLayer[id].getBounds());
		}
	}

	if(bbox){
		getRectangle(bbox);
		el.attr('value', bbox);
		lastBbox = bbox;
		manageControl(drawControlEditOnly, drawControl);
		ShowHide('.edit-group', '.draw-group');
	} else {
		el.removeAttr('value');
		ShowHide('.draw-group','.edit-group');
	}


	editDrawControl();

})