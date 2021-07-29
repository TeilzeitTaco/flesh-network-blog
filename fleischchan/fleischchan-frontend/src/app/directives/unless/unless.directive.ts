import {Directive, Input, TemplateRef, ViewContainerRef} from '@angular/core';


// NOTE: There is also a NG switch directive

@Directive({
  selector: '[appUnless]'
})
export class UnlessDirective {
  // DI-like injection
  constructor(private templateRef: TemplateRef<any>, private viewContainerRef: ViewContainerRef) { }

  // This is a set-only property
  @Input() set unless(condition: boolean) {
    if (!condition) {
      this.viewContainerRef.createEmbeddedView(this.templateRef)
    } else {
      this.viewContainerRef.clear()
    }
  }
}
