#import <Cocoa/Cocoa.h>
#import <PDFKit/PDFKit.h>
int main(int argc, const char **argv) {
 @autoreleasepool {
  if(argc != 3) return 2;
  PDFDocument *doc = [[PDFDocument alloc] initWithURL:[NSURL fileURLWithPath:@(argv[1])]];
  if(!doc) return 3;
  NSString *out = @(argv[2]);
  [[NSFileManager defaultManager] createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:nil];
  for(NSUInteger i=0;i<doc.pageCount;i++) {
   PDFPage *page=[doc pageAtIndex:i]; NSRect r=[page boundsForBox:kPDFDisplayBoxMediaBox];
   CGFloat scale=1280/r.size.width; NSInteger w=1280,h=(NSInteger)(r.size.height*scale);
   NSBitmapImageRep *rep=[[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:w pixelsHigh:h bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
   [NSGraphicsContext saveGraphicsState]; NSGraphicsContext *ctx=[NSGraphicsContext graphicsContextWithBitmapImageRep:rep]; [NSGraphicsContext setCurrentContext:ctx];
   CGContextSetRGBFillColor(ctx.CGContext,1,1,1,1); CGContextFillRect(ctx.CGContext,CGRectMake(0,0,w,h)); CGContextScaleCTM(ctx.CGContext,scale,scale);
   [page drawWithBox:kPDFDisplayBoxMediaBox toContext:ctx.CGContext]; [NSGraphicsContext restoreGraphicsState];
   NSData *data=[rep representationUsingType:NSBitmapImageFileTypePNG properties:@{}];
   [data writeToFile:[out stringByAppendingPathComponent:[NSString stringWithFormat:@"page-%02lu.png",(unsigned long)i+1]] atomically:YES];
  }
  printf("Rendered %lu pages\n",(unsigned long)doc.pageCount);
 }
 return 0;
}
