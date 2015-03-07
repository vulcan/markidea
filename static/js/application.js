/*
 * mark the markdown title menu
 * jquery is required
 * the titles is a list for jquery selected object that following the document flow order
 * h1 - h6
 * @param container: the container that hold the titles
 * */
function buildMenuTree(container) {
	var stack = new Array(); //stack operation holder
    var root = {tagName:'H', text: 'Content', nodes:[], href:'#anchor_0'};
	stack.push(root);
	// walk through the titles
    var titles = $('h1,h2,h3,h4,h5,h6', container);
	var counter = 1;
    titles.each(function(){
		// get current node's
		var tagName = this.tagName.toUpperCase();
		var cur = stack[stack.length - 1]; // the last one
		while(tagName <= cur.tagName) {
			stack.pop(); // pop up the last until get the insert point
			cur = stack[stack.length - 1];
		}
		if (tagName > cur.tagName) {
            var node = {tagName:tagName, text:$(this).text(), nodes:[], href:'#anchor_'+counter};
			cur.nodes.push(node);
			stack.push(node); // push to the stack
			$(this).wrapInner("<a name='anchor_"+counter+"'></a>")
			// increase the counter
			counter++;
		}
        });
	// the root node should be fullfilled
	return root;
}
/**
 * 获取路径中的父目录
 */
function basename(path)
{
    var slash_pos = path.lastIndexOf('/');
    if (slash_pos > 0) {
        return path.substring(0, slash_pos);
    }
    return "";
}
/**
 * 获取路径中的扩展名
 */
function extname(path) {
    var dot_pos = path.lastIndexOf('.');
    if (dot_pos > 0) {
        return path.substring(dot_pos);
    }
    return "";
}
