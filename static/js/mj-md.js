const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const form = document.getElementById('form');

// Define your data
let data = {
    "filename": "Top_10_Upf_T-Shirts_For_Ultimate_Sun_Protection_Test.txt",
    "file_path": "/Users/yansir/Library/Mobile Documents/com~apple~CloudDocs/Documents/github-projects/yansir-pythonanywhere/routes/tmp/Top_10_Upf_T-Shirts_For_Ultimate_Sun_Protection_Test.txt",
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
form.addEventListener('submit', function(e) {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = '';
    e.preventDefault();
    var formData = new FormData(this);
    axios.post('/fio_imgs', formData)
    .then(response => {
        const data = response.data;
        data.imgs[0].forEach((messageId, i) => {
            // Create section
            const sectionDiv = document.createElement('div');
            sectionDiv.id = `section-${i+1}`;
            sectionDiv.className = 'section';

            // Create title
            const title = document.createElement('h3');
            title.id = `section-${i+1}-title`;
            title.className = 'section-title';
            title.innerText = data.imgs[2][i];  
            sectionDiv.appendChild(title);

            // Create description
            const description = document.createElement('p');
            description.id = `section-${i+1}-description`;
            description.className = 'section-description';
            description.innerText = data.imgs[3][i];
            sectionDiv.appendChild(description);

            // Create progress bar
            const progressBar = document.createElement('div');
            progressBar.id = `progress-bar-${i+1}`;
            progressBar.className = 'progress-bar';
            sectionDiv.appendChild(progressBar);

            // Create image container
            const imageContainer = document.createElement('div');
            imageContainer.id = `image-container-${i+1}`;
            imageContainer.className = 'image-container';
            sectionDiv.appendChild(imageContainer);

            // Create choose button
            const selectList = document.createElement('select');
            selectList.id = `image-select-${i+1}`;
            sectionDiv.appendChild(selectList);

            // Append section to resultsContainer
            resultsContainer.appendChild(sectionDiv);

            // if the imageContainer.firstchild.src exist and end with png, then append the image
            if(imageContainer.firstChild && imageContainer.firstChild.src.endsWith('png')) {
                let intervalId = setInterval(() => {
                    axios.get(`https://api.thenextleg.io/v2/message/${messageId}?expireMins=12`, {
                        headers: { 
                            'Authorization': 'Bearer 5b107ade-df55-416b-86bb-939d68971613', 
                            'Access-Control-Allow-Origin': 'no-cors',
                        }
                    })
                    .then(response => {
                        const progressData = response.data;
                        progressBar.style.width = progressData.progress + "%";
                        // Create tempImg to show progress
                        if (progressData.progressImageUrl){
                            let tempImg = document.createElement('img');
                            tempImg.src = progressData.progressImageUrl;
                            // Set the src of the first img in the imageContainer to the progress image
                            imageContainer.firstChild ? imageContainer.firstChild.src = progressData.progressImageUrl : imageContainer.appendChild(tempImg);
                        }
                        if (progressData.progress === 100) {
                            clearInterval(intervalId);
                            imageContainer.firstChild.src = progressData.response.imageUrl;
                            progressBar.style.display = 'none';

                            progressData.response.imageUrls.forEach((url, index) => { 
                                // Create new select option
                                let option = document.createElement('option');
                                option.value = url;
                                option.text = `选第 ${index + 1} 张`;
                                // Default select the first option
                                if(index === 0) {
                                    option.selected = true;
                                }
                                selectList.appendChild(option);
                            });  
                        }
                    })
                    .catch((error) => {
                        console.error(error);
                    });
                }, 3000);
            }
            // Create submit button outside of forEach loop
            if(i === data.imgs[0].length - 1) {
                const submitButton = document.createElement('button');
                submitButton.innerText = '提交';
                submitButton.className = 'submit-button';
                resultsContainer.appendChild(submitButton);
                loader.style.display = 'none';
                
                submitButton.addEventListener('click', () => {
                    loader.style.display = 'block';
                    let selectedImages = Array.from(document.querySelectorAll('select')).map((select, i) => {
                        return {
                            'upscale_img_name': data.imgs[1][i],
                            'upscale_img_alt': data.imgs[2][i],
                            'upscale_img_url': select.value
                        };
                    });
                    
                    let payload = {
                        'filename': data.filename,
                        'file_path': data.file_path,
                        'imgs': selectedImages
                    }
                
                    axios.post('/mj_to_md', payload, {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => {
                        const data = response.data;
                        const textData = data.content;
                        const blob = new Blob([textData], {type: "text/plain"});
                        const url = URL.createObjectURL(blob);

                        const buttonContainer = document.createElement('div');
                        buttonContainer.className = 'button-container';

                        const downloadButton = document.createElement('button');
                        downloadButton.className = 'download-button';
                        downloadButton.innerText = "下载文档";
                        downloadButton.addEventListener('click', () => {
                            const hiddenElement = document.createElement('a');
                            hiddenElement.href = url;
                            hiddenElement.target = '_blank';
                            hiddenElement.download = data.filename;
                            hiddenElement.click();
                        });

                        const uploadButton = document.createElement('button');
                        uploadButton.className = 'upload-button';
                        uploadButton.innerText = "上传WP";
                        uploadButton.addEventListener('click', () => {
                            loader.style.display = 'block';
                            payload = {
                                'filename': data.filename,
                                'file_path': data.file_path,
                            }
                            axios.post('/upload_to_wp', payload, {
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => {
                                const data = response.data;
                                const successMessage = document.createElement('span');
                                successMessage.innerText = '上传成功！';
                                resultsContainer.innerHTML = '';
                                //clear the file in the form filed
                                form.reset();
                                resultsContainer.appendChild(successMessage);
                                loader.style.display = 'none';
                            })
                            .catch((error) => {
                                console.error(error);
                            });
                        });
                        
                        buttonContainer.appendChild(downloadButton);
                        buttonContainer.appendChild(uploadButton);
                        resultsContainer.appendChild(buttonContainer);
                        loader.style.display = 'none';
                    })
                    .catch((error) => {
                        console.error(error);
                    });
                });        
            }
        });
    });
});
