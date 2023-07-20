const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const form = document.getElementById('form');

// Define your data
let data = {
    "raw_content": "...",
    "imgs": [
        [
            "jPqaXdCJ0PUGZ0JQpx0z",
            "6b13jQh4PMSoMB1XosIq",
            "mPFx85KGF4powWFW6sxY",
            "NsJeyrY331vt80eKVJ8P",
            "M37diFRA1KBVOOmmA2kL"
        ],
        [
            "upf_tshirt.png",
            "upf_tshirt.png",
            "fashion_meets_function.png",
            "upf_tshirt.png",
            "sunscreen.png"
        ],
        [
            "UPF fabric t-shirt",
            "UPF fabric t-shirt",
            "Fashion meets function clothing",
            "UPF fabric t-shirt",
            "Sunscreen and protective accessories"
        ],
        [
            "msg1",
            "msg2",
            "msg3",
            "msg4",
            "msg5"
        ]
    ]
};

// Start to load sections after the data returned.

data.imgs[0].forEach((messageId, i) => {
    // Create section
    const sectionDiv = document.createElement('div');
    sectionDiv.id = `section${i+1}`;
    sectionDiv.className = 'section';

    // Create title
    const title = document.createElement('h3');
    title.id = `section${i+1}-title`;
    title.className = 'section-title';
    title.innerText = data.imgs[2][i];  
    sectionDiv.appendChild(title);

    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.id = `progress-bar${i+1}`;
    progressBar.className = 'progress-bar';
    sectionDiv.appendChild(progressBar);

    // Create image container
    const imageContainer = document.createElement('div');
    imageContainer.id = `image-container${i+1}`;
    imageContainer.className = 'image-container';
    sectionDiv.appendChild(imageContainer);

    // Append section to resultsContainer
    resultsContainer.appendChild(sectionDiv);

    fetch(`https://api.thenextleg.io/v2/message/${messageId}?expireMins=2`, {
        headers: { 
            'Authorization': 'Bearer 5b107ade-df55-416b-86bb-939d68971613', 
        }
    })
    .then(response => response.json())
    .then((progressData) => {
        progressBar.style.width = progressData.progress + "%";

        if (progressData.progress === 100) {
            progressData.response.imageUrls.forEach((url) => {
                var img = document.createElement('img');
                img.src = url;
                imageContainer.appendChild(img);
            });
        }
    })
    .catch((error) => {
        console.error(error);
    });
});
