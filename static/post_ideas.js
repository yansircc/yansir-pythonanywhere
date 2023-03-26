(function ($) {
	$(document).ready(function(){
		if(localStorage.getItem('dataTrained') === null){
			alert("请先进行预训练，不然结果不准。");
		}else{
			let dataTrained = localStorage.getItem('dataTrained');
			let container = document.getElementById('response-container');
			let loader = document.getElementById('loader');
			// Send dataTrained to server side using AJAX
			$.ajax({
				url: "/post-ideas",
				type: "POST",
				data: JSON.stringify({user_trianed_data: dataTrained}),
				contentType: "application/json",
				success: function(response) {
					console.log("DataTrained sent successfully");
				},
				error: function(xhr, status, error) {
					console.log("An error occurred while sending dataTrained: " + error);
				}
			});
			$("#query-form").submit(function(event){
				event.preventDefault();
				let keyword = $("#keyword").val().split('\n');
				let process = $("#process").val().split('\n');
                let data = [];
				for (let i = 0; i < keyword.length; i++) {
					for (let j = 0; j < process.length; j++) {
						data.push("If '" + keyword[i] + "' and '" + process[j] + "' combine, what B2B blog article can you write?");
					}
				}

				function sendData(index) {
					if (index >= data.length) {
						return;
					}
					loader.style.display = "block";
					$.ajax({
						url: "/post-ideas",
						type: "POST",
						data: JSON.stringify({client_request: data[index]}),
						contentType: "application/json",
						success: function(response) {
       container.innerHTML += '<div class="blog-title-idea"><span class="highlight">' + response + '</span><div class="download-buttons"><button class="response-post-download">下载问答文章</button><button class="listicle-download">下载列表文章</button><button class="pillar-post-download">下载论文文章</button></div></div>';
							container.style.display = "block";
							loader.style.display = "none";
							sendData(index + 1); // Call the function again with the next index
						},
						error: function(xhr, status, error) {
							console.log("An error occurred: " + error);
						}
					});
				}
				sendData(0);
			});
		}
	});
})(jQuery);