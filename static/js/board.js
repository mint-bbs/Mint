let board = location.pathname.split("/")[1];

async function refreshThreads(threads) {
  const threadsElement = document.getElementById("threadsList");
  let count = 0;
  threads.forEach((thread) => {
    count++;
    let node = document.createElement("a");
    node.href = `/test/read.cgi/${thread.board}/${thread.id}/`;
    node.textContent = `${count}: ${thread.title}(${thread.count})`;
    threadsElement.append(node);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("formBoard").value = board;

  let response = await fetch(`/api/boards/${board}/threads`);
  let threads = await response.json();
  console.log(threads);
  await refreshThreads(threads);
});
