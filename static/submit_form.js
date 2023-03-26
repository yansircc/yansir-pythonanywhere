(function ($) {
    function getClientIdFromCookie() {
        let gaCookie = document.cookie.split('; ').find(row => row.startsWith('_ga='));
        if (gaCookie) {
            return gaCookie.split('=')[1].split('.').slice(2).join('.');
        }
        return null;
    }

    $(document).ready(function () {
        $('form').submit(function (event) {
            event.preventDefault();
            const formData = $(this).serialize(); // Get form data
            const leads_content = formData;
            const sys_prompt = "You're a rating machine. You will rate the inquiries on a scale of 0-100. If the inquiry has no relationship with B2B procurement, you will give it a rating of 0. If it is relevant, then you will rate it based on the quality of the inquiry. You always output score first head and then explain the reasons.";
            const max_tokens = 100;
            const temperature = 0.1;
            const measurement_id = "G-RPRHNJS8XP";
            const api_secret = "wmZ8kj6QQde3CvKez_PoQQ";
            const ads_conversion_id = "AW-756055019/YmB9CNmLvpIYEOv3wegC";
            const client_id = getClientIdFromCookie();

            $.ajax({
                url: "http://127.0.0.1:5000/leads-value",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    leads_content: leads_content,
                    sys_prompt: sys_prompt,
                    measurement_id: measurement_id,
                    api_secret: api_secret,
                    max_tokens: max_tokens,
                    temperature: temperature,
                    ads_conversion_id: ads_conversion_id,
                    client_id: client_id
                }),
                success: function (response) {
                    console.log(response);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error("Error: ", errorThrown);
                },
            });
            return false;
        });
    });
})(jQuery);
