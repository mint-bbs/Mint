const threads = [];

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
    threads.push(response);

    const node = document.createElement("div");
    node.classList.add("thread");

    const date = new Date(response.created_at);
    if (response.count == 1) {
      document.querySelector(".thread-title").textContent = response.title;
      returnDate = date;
    }
    node.innerHTML = `${response.count}：<span style="color: green;"><b>${
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
});
