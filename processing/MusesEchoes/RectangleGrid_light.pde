float x;
float y;
int pixdim = 1;

void setup() {
  
  size(640,300);
  background(0);
  
}

void draw() {

  for(x=0; x<width; x=x+pixdim){    
    for(y=0; y<height; y=y+pixdim){
      //mouseX - pixdim/2 as a translation in a function
      fill(255* 1/(dist(x, y, mouseX - pixdim/2, mouseY - pixdim/2)/(sqrt(sq(width) + sq(height))) +1));
      if(mousePressed)
      fill(255* 1/(dist(x, y, mouseX - pixdim/2, mouseY - pixdim/2)/(sqrt(width + height)) +1));
      noStroke();
      rect(x, y, pixdim, pixdim);
    }
  }
  
}
