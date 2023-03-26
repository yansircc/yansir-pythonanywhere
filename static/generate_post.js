(function ($) {
  function handleDownload(postType) {
    let title = $(this).parent().siblings('.highlight').text();
    let loader = document.getElementById("loader");
    let dataTrained = localStorage.getItem('dataTrained');
    loader.style.display = "block";
    $.ajax({
      beforeSend: function() {
        showToast('正在制作PDF', 3000);
      },
      type: "POST",
      url: '/convert-to-md',
      data: JSON.stringify({title: title, postType: postType, dataTrained: dataTrained}),
      contentType: "application/json",
      success: function(responseMarkdown) {
        let markdown_string = responseMarkdown.markdown_string;
        $.ajax({
          type: "POST",
          url: '/download-pdf',
          data: JSON.stringify({markdown_string: markdown_string, title: title}),
          contentType: "application/json",
          success: function(responsePdf) {
            let downloadUrl = responsePdf.download_url;
            let downloadLink = document.createElement('a');
            downloadLink.href = downloadUrl;
            downloadLink.download = "output.pdf";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            loader.style.display = "none";
          }
        });
      }
    });
  }

  function showToast(message, duration) {
    let toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '50%';
    toast.style.left = '50%';
    toast.style.transform = 'translate(-50%, -50%)';
    toast.style.backgroundColor = '#23a455';
    toast.style.color = '#fff';
    toast.style.padding = '10px';
    toast.style.fontSize = '12px';
    toast.style.borderRadius = '20px';
    // Fade in the toast
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.5s ease-in';
    setTimeout(function () {
      toast.style.opacity = '1';
    }, 0);

    // Fade out the toast
    setTimeout(function () {
      toast.style.opacity = '0';
    }, duration - 500);

    setTimeout(function () {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, duration);
    toast.style.zIndex = '1000';
  
    document.body.appendChild(toast);
    setTimeout(function () {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, duration);
  }

  $(document).on('click', '.response-post-download', function() {
    handleDownload.call(this, 'response-post');
  });

  $(document).on('click', '.listicle-download', function() {
    handleDownload.call(this, 'listicle');
  });

  $(document).on('click', '.pillar-post-download', function() {
    handleDownload.call(this, 'pillar-post');
  });
})(jQuery);
