import {Directive, ElementRef, OnInit} from "@angular/core";

@Directive({
  selector: '[appBasicHighlight]'
})
export class BasicHighlightDirective implements OnInit {
  constructor(private elementRef: ElementRef) {}

  ngOnInit(): void {
    // NOTE: Bad because direct access. Don't do this.
    this.elementRef.nativeElement.style.backgroundColor = 'green';
  }
}
