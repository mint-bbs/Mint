const cachedResponses = [];

let board = location.pathname.split("/")[3];
let key = location.pathname.split("/")[4];

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function formatDate(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  const milliseconds = String(date.getMilliseconds()).padStart(3, "0");
  const week = ["日", "月", "火", "水", "木", "金", "土"];
  const w = week[date.getDay()];

  return `${yyyy}/${mm}/${dd}(${w}) ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

async function refreshThread(responses) {
  const progressBar = document.getElementById("progress");

  const responsesElement = document.querySelector(".responses");

  let count = 0;
  const nodes = [];

  var returnDate = new Date();

  responses.forEach((response) => {
    count += 1;
    cachedResponses.push(response);

    const node = document.createElement("div");
    node.classList.add("thread");

    const date = new Date(response.created_at);
    if (count == 1) {
      document.querySelector(".thread-title").textContent = response.title;
      returnDate = date;
    }
    node.innerHTML = `${count}：<span style="color: green;"><b>${
      response.name
    }</b></span>：${formatDate(date)} ID: ${response.account_id}`;

    const content = document.createElement("div");
    content.classList.add("content");
    content.innerHTML = response.content;
    node.append(content);

    nodes.push(node);

    progressBar.value = count;
  });

  responsesElement.innerHTML = "";
  nodes.forEach((node) => responsesElement.appendChild(node));
  progressBar.remove();
  return returnDate;
}

async function post(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    name: formData.get("name"),
    authKey: formData.get("authKey"),
    content: formData.get("content"),
  };
  response = await fetch(`/api/boards/${board}/threads/${key}`, {
    method: "put",
    headers: {
      "content-type": "application/json",
      Cookie: `2ch_X=${getCookie("2ch_X")}`,
    },
    body: JSON.stringify(body),
  });
  try {
    jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      document.cookie = response.headers.cookie;

      bulmaToast.toast({
        message: "スレッドに書き込みました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-left",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        e.target.querySelector("input[name=name]").value = "";
        e.target.querySelector("input[name=authKey]").value = "";
        e.target.querySelector("textarea[name=content]").value = "";
        submit.disabled = false;
      }, 1000);
    } else {
      bulmaToast.toast({
        message: jsonData.detail,
        type: "is-danger",
        duration: 5000,
        dismissible: true,
        pauseOnHover: true,
        position: "top-left",
        closeOnClick: true,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        submit.disabled = false;
      }, 1000);
    }
  } catch {
    bulmaToast.toast({
      message: "不明なエラーが発生しました。",
      type: "is-danger",
      duration: 5000,
      dismissible: true,
      pauseOnHover: true,
      position: "top-left",
      closeOnClick: true,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    setTimeout(function () {
      submit.disabled = false;
    }, 1000);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const progressBar = document.getElementById("progress");

  const response = await fetch(`/api/boards/${board}/threads/${key}`);
  const data = await response.text();
  const responses = JSON.parse(data);
  console.log(responses);
  progressBar.max = responses.length;
  date = await refreshThread(responses);

  document.querySelector(".size").textContent = `${data.length}KB`;

  let nowDate = new Date();
  nowTime = (nowDate.getTime() - date.getTime()) / 1000 / 60;
  ikioi = (responses.length / nowTime) * 60 * 24;
  document.getElementById("ikioi").textContent = `勢い: ${ikioi}`;

  const postForm = document.getElementById("postForm");
  postForm.addEventListener("submit", post);
});
