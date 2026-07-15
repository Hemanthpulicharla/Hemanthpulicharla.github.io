document.addEventListener("DOMContentLoaded", function() {
  // Initialize KaTeX for math rendering
  if (typeof renderMathInElement !== 'undefined') {
    renderMathInElement(document.body, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false}
      ]
    });
  }
  
  // Initialize Mermaid for diagrams
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({startOnLoad: true});
  }
  
  // Email obfuscation (customize as needed)
  let element = document.getElementById("my-addr");
  if (element) {
    let eaddr = "hemanth.pulicharlaa" + "[at]" + "gmail.com";
    element.innerHTML = "<a href='mailto:" + eaddr.replace("[at]", "@") + "'>" + eaddr + "</a>";
  }
});