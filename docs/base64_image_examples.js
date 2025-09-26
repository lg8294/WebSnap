// Base64图片显示示例

// 1. 基本用法 - 在img标签中显示
function displayBase64Image(base64Data) {
  const img = document.createElement("img");
  img.src = "data:image/png;base64," + base64Data;
  img.alt = "网页截图";
  document.body.appendChild(img);
}

// 2. 在现有img元素中显示
function updateImageElement(imgElement, base64Data) {
  imgElement.src = "data:image/png;base64," + base64Data;
}

// 3. 创建可下载的图片
function createDownloadableImage(base64Data, filename = "screenshot.png") {
  const img = document.createElement("img");
  img.src = "data:image/png;base64," + base64Data;
  img.style.cursor = "pointer";
  img.title = "点击下载图片";

  img.addEventListener("click", function () {
    const link = document.createElement("a");
    link.download = filename;
    link.href = img.src;
    link.click();
  });

  return img;
}

// 4. 在Canvas中显示base64图片
function drawBase64ImageOnCanvas(canvasId, base64Data) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext("2d");
  const img = new Image();

  img.onload = function () {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
  };

  img.src = "data:image/png;base64," + base64Data;
}

// 5. 使用fetch API获取截图并显示
async function fetchAndDisplayScreenshot(url, options = {}) {
  try {
    const response = await fetch("http://localhost:9000/screenshot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: url,
        wait_time: options.waitTime || 3,
        full_page: options.fullPage !== false,
        viewport_width: options.viewportWidth || 1920,
        viewport_height: options.viewportHeight || 1080,
        format: "base64",
      }),
    });

    const data = await response.json();

    if (data.success) {
      // 显示图片
      displayBase64Image(data.screenshot);

      // 或者创建可下载的图片
      const downloadableImg = createDownloadableImage(
        data.screenshot,
        `screenshot_${Date.now()}.png`
      );
      document.body.appendChild(downloadableImg);

      return data;
    } else {
      console.error("截图失败:", data.error);
      return null;
    }
  } catch (error) {
    console.error("请求失败:", error);
    return null;
  }
}

// 6. 批量截图并显示
async function batchScreenshots(urls) {
  const results = [];

  for (const url of urls) {
    console.log(`正在截图: ${url}`);
    const result = await fetchAndDisplayScreenshot(url);
    results.push({ url, result });

    // 添加延迟避免请求过于频繁
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  return results;
}

// 7. 创建图片画廊
function createImageGallery(screenshots) {
  const gallery = document.createElement("div");
  gallery.style.display = "grid";
  gallery.style.gridTemplateColumns = "repeat(auto-fit, minmax(300px, 1fr))";
  gallery.style.gap = "20px";
  gallery.style.padding = "20px";

  screenshots.forEach((screenshot, index) => {
    const card = document.createElement("div");
    card.style.border = "1px solid #ddd";
    card.style.borderRadius = "8px";
    card.style.overflow = "hidden";
    card.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";

    const img = document.createElement("img");
    img.src = "data:image/png;base64," + screenshot.base64Data;
    img.style.width = "100%";
    img.style.height = "auto";
    img.style.display = "block";

    const caption = document.createElement("div");
    caption.style.padding = "10px";
    caption.style.backgroundColor = "#f8f9fa";
    caption.textContent = `截图 ${index + 1}: ${screenshot.url}`;

    card.appendChild(img);
    card.appendChild(caption);
    gallery.appendChild(card);
  });

  return gallery;
}

// 8. 使用示例
document.addEventListener("DOMContentLoaded", function () {
  // 示例：截图并显示
  const exampleButton = document.createElement("button");
  exampleButton.textContent = "截图示例";
  exampleButton.onclick = function () {
    fetchAndDisplayScreenshot("https://platform.kangfx.com", {
      waitTime: 3,
      fullPage: true,
      viewportWidth: 1280,
      viewportHeight: 720,
    });
  };
  document.body.appendChild(exampleButton);
});

// 导出函数供其他模块使用
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    displayBase64Image,
    updateImageElement,
    createDownloadableImage,
    drawBase64ImageOnCanvas,
    fetchAndDisplayScreenshot,
    batchScreenshots,
    createImageGallery,
  };
}
