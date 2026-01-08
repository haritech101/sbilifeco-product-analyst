const apiUrl = "${API_BASE_URL}${API_INGEST_PATH}";

const inputContentName = document.getElementById(
    "input-content-name"
) as HTMLInputElement;
const inputContentFile = document.getElementById(
    "input-content-file"
) as HTMLInputElement;
const actionUpload = document.getElementById(
    "action-upload"
) as HTMLButtonElement;
const bannerFeedbackUpload = document.getElementById(
    "banner-feedback-upload"
) as HTMLDivElement;

const leaveFeedback = (
    feedback: string,
    isError: boolean = false,
    isSuccess: boolean = false
) => {
    bannerFeedbackUpload.innerText = feedback;

    if (isError) {
        bannerFeedbackUpload.classList.add("text-danger");
        bannerFeedbackUpload.classList.remove("text-success");
    } else if (isSuccess) {
        bannerFeedbackUpload.classList.remove("text-danger");
        bannerFeedbackUpload.classList.add("text-success");
    } else {
        bannerFeedbackUpload.classList.remove("text-danger");
        bannerFeedbackUpload.classList.remove("text-success");
    }
};

const processUpload = async () => {
    console.log(`Requesting an ingestion session`);

    let req = new Request(apiUrl, { method: "POST" });
    let res = await fetch(req);
    if (!res.ok) {
        leaveFeedback(
            `Upload failed with status ${(await res.text()) || res.status}`,
            true
        );
        return;
    }

    let api_response = await res.json();
    if (api_response?.is_success !== true) {
        leaveFeedback(
            `Upload failed: ${api_response?.message || "Unknown error"}`,
            true
        );
        return;
    }

    const ingest_request_id = api_response.payload;
    console.log(`Ingestion session acquired`);

    console.log(`Posting content`);
    const dataToPost = new FormData();
    dataToPost.set("title", inputContentName?.value || "");
    dataToPost.set(
        "material",
        inputContentFile?.files?.[0] ||
            new Blob([], { type: "application/octet-stream" })
    );

    req = new Request(`${apiUrl}/${ingest_request_id}`, {
        method: "POST",
        body: dataToPost,
    });

    res = await fetch(req);
    if (!res.ok) {
        leaveFeedback(
            `Upload failed with status ${(await res.text()) || res.status}`,
            true
        );
        return;
    }

    api_response = await res.json();
    if (api_response?.is_success !== true) {
        leaveFeedback(
            `Upload failed: ${api_response?.message || "Unknown error"}`,
            true
        );
        return;
    }

    console.log(`Content uploaded successfully`);
    leaveFeedback("Upload successful!", false, true);

    inputContentName.value = "";
    inputContentFile.value = "";
};

const onUploadTriggered = async () => {
    const contentName = inputContentName.value;
    const contentFile = inputContentFile.files?.[0];

    if (!contentName) {
        leaveFeedback("Please enter a valid content name.", true);
        return;
    }

    if (!contentFile) {
        leaveFeedback("Please select a file to upload.", true);
        return;
    }

    leaveFeedback(`Processing upload of "${contentName}"...`);
    await processUpload();
};

actionUpload.addEventListener("click", async () => {
    await onUploadTriggered();
});
