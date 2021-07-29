import {Directive, ElementRef, HostBinding, HostListener, OnInit, Renderer2, RendererStyleFlags2} from '@angular/core';

@Directive({
  selector: '[appBetterHighlight]'
})
export class BetterHighlightDirective implements OnInit {
  // JS events
  @HostListener("mouseenter") mouseOver() {
    // this.renderer.setStyle(this.elementRef.nativeElement, 'background-color', 'blanchedalmond')
    this.backgroundColor = "blanchedalmond";
  }

  @HostListener("mouseleave") mouseleave() {
    this.backgroundColor = "green";
  }

  // NOTE: Two ways to do this, prop binding or renderer. Prefer prop binding

  // DOM property not CSS property (the way it is referenced via JS)
  @HostBinding('style.backgroundColor') backgroundColor: string | undefined;

  constructor(private elementRef: ElementRef, private renderer: Renderer2) { }

  ngOnInit(): void {
    // this.renderer.setStyle(this.elementRef.nativeElement, 'background-color', 'transparent', RendererStyleFlags2.Important)
    this.backgroundColor = "transparent"
  }
}
