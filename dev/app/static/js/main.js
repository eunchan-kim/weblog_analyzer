(function(){
var t;
function size(animate){
	if (animate == undefined){
		animate = false;
	}
	clearTimeout(t);
	t = setTimeout(function(){
		$("canvas").each(function(i,el){
			$(el).attr({
				"width":$(el).parent().width(),
				"height":$(el).parent().outerHeight()
			});
		});
		redraw(animate);
		var m = 0;
		$(".widget").height("");
		$(".widget").each(function(i,el){ m = Math.max(m,$(el).height()); });
		$(".widget").height(m);
	}, 30);
}
$(window).on('resize', function(){ size(false); });


function redraw(animation){
	var options = {};
	if (!animation){
		options.animation = false;
	} else {
		options.animation = true;
	}
	var data = [
		{
			value: 20,
			color:"#637b85"
		},
		{
			value : 30,
			color : "#2c9c69"
		},
		{
			value : 40,
			color : "#dbba34"
		},
		{
			value : 10,
			color : "#c62f29"
		}

	];
	var canvas = $("#hours");
	var ctx = canvas.getContext("2d");
	new Chart(ctx).Doughnut(data, options);

        var l = [];
	var d = [];
	{% for elem in data %}
	  l.push("{{ elem.ip }}")
	  d.push({{ elem.num }})
	{% endfor %}

	var data = {
		labels : l,
		datasets : [
			{
				fillColor : "rgba(99,123,133,0.4)",
				strokeColor : "rgba(220,220,220,1)",
				pointColor : "rgba(220,220,220,1)",
				pointStrokeColor : "#fff",
				data : d
			}
		]
	}
	var canvas = $("#shipments");
	var ctx = canvas.getContext("2d");
	new Chart(ctx).Bar(data, options);



	var data = {
		labels : ["Helpful","Friendly","Kind","Rude","Slow","Frustrating"],
		datasets : [
			{
				fillColor : "rgba(220,220,220,0.5)",
				strokeColor : "#637b85",
				pointColor : "#dbba34",
				pointStrokeColor : "#637b85",
				data : [65,59,90,81,30,56]
			}
		]
	}
	var canvas = $("departments");
	var ctx = canvas.getContext("2d");
	new Chart(ctx).Radar(data, options);
}
size(true);

}());
