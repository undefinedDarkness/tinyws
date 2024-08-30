from tinyws import Webview
import pathlib

script_dir = pathlib.Path(__file__).parent.resolve()
wv = Webview(window_type=4, decorated=False, transparent=True, width='512', height='512', html="""

<!DOCTYPE HTML>
<html>
<head>
<style>
    html, body {
        background: rgba(255,255,255,0.75);
        color: #f0f0f0;
    }

html { height: 100%; }

body {
  min-height: 100%;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: white;
  font-family: sans-serif;
  text-align: center;
}

.illo {
  display: block;
  cursor: move;
}
</style>
</head>
<body>

<div class="container">
  <canvas class="illo"></canvas>
</div>

<script src="https://unpkg.com/zdog@1/dist/zdog.dist.js"></script>
<script>
// Made with Zdog

// ----- setup ----- //

var sceneSize = 24;
var TAU = Zdog.TAU;

var illo = new Zdog.Illustration({
  element: '.illo',
  rotate: { x: TAU * -35/360, y: TAU * 1/8 },
  dragRotate: true,
  resize: 'fullscreen',
  onResize: function( width, height ) {
    this.zoom = Math.floor( Math.min( width, height ) / sceneSize );
  },
});

// ----- model ----- //

var cube = new Zdog.Anchor({
  addTo: illo,
  scale: 4,
});

var oneUnit = new Zdog.Vector({ x: 1, y: 1 });

var side = new Zdog.Anchor({
  addTo: cube,
  translate: { z: 1 },
});

var dot = new Zdog.Shape({
  addTo: side,
  translate: oneUnit.copy(),
  stroke: 1,
  color: 'black',
});

dot.copy({ translate: { x: -1, y:  1 } });
dot.copy({ translate: { x:  1, y: -1 } });
dot.copy({ translate: { x: -1, y: -1 } });

// more dots
dot.copy({ translate: { x:  1 } });
dot.copy({ translate: { x: -1 } });
dot.copy({ translate: { y: -1 } });
dot.copy({ translate: { y:  1 } });

side.copyGraph({
  translate: { z: -1 },
});

var midDot = dot.copy({
  addTo: cube,
});

midDot.copy({ translate: { x: -1, y:  1 }} );
midDot.copy({ translate: { x:  1, y: -1 }} );
midDot.copy({ translate: { x: -1, y: -1 }} );


// ----- animate ----- //

var keyframes = [
  { x: 0, y: 0, z: 0 },
  { x: 0, y: 0, z: TAU/4 },
  { x: -TAU/4, y: 0, z: TAU/4 },
  { x: -TAU/4, y: 0, z: TAU/2 },
];

var ticker = 0;
var cycleCount = 75;
var turnLimit = keyframes.length - 1;

function animate() {
  var progress = ticker / cycleCount;
  var tween = Zdog.easeInOut( progress % 1, 4 );
  var turn = Math.floor( progress % turnLimit );
  var keyA = keyframes[ turn ];
  var keyB = keyframes[ turn + 1 ];
  cube.rotate.x = Zdog.lerp( keyA.x, keyB.x, tween );
  cube.rotate.y = Zdog.lerp( keyA.y, keyB.y, tween );
  cube.rotate.z = Zdog.lerp( keyA.z, keyB.z, tween );
  ticker++;

  illo.updateRenderGraph();
  requestAnimationFrame( animate );
}

animate();


</script>
</body>
</html>

""")


wv.run()
