const s = require("fs").readFileSync("D:/Coding/lurenjia_mianshi/assets/docsify.js", "utf8");
const m = s.match(/version:\s*["']([^"']+)["']/);
console.log("docsify version:", m ? m[1] : "unknown");
console.log("has doneEach:", s.includes("doneEach"));
console.log("has mounted:", s.includes("mounted"));
console.log("has afterEach:", s.includes("afterEach"));
