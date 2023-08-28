import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import mermaid from 'mermaid';

@Component({
  selector: 'app-agents-seqdiagrams',
  templateUrl: './agents-seqdiagrams.component.html',
  styleUrls: ['./agents-seqdiagrams.component.css']
})
export class AgentsSeqdiagramsComponent implements OnInit {

  @ViewChild('mermaidDivGreen', { static: false }) mermaidDivGreen: ElementRef;
  @ViewChild('mermaidDivRed', { static: false }) mermaidDivRed: ElementRef;
  @ViewChild('mermaidDivBlue', { static: false }) mermaidDivBlue: ElementRef;

  // TODO: dynamic sequence diagram
  secondGraphDefinition = `sequenceDiagram
    box Purple Alice & John
    participant A
    participant J
    end
    box Another Group
    participant B
    participant C
    end
    A->>J: Hello John, how are you?
    J->>A: Great!
    A->>B: Hello Bob, how is Charly ?
    B->>C: Hello Charly, how are you?
    `;

  firstGraphDefinition = `sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
    `;

  greenSeqDef = this.firstGraphDefinition
  redSeqDef = this.firstGraphDefinition
  blueSeqDef = this.firstGraphDefinition

  public ngAfterViewInit(): void {

    this.updateSeq();

  }

  ngOnInit(): void {
    mermaid.initialize({
      securityLevel: 'loose'
    });
    mermaid.init();

    // setTimeout(() => {
    //   this.greenSeqDef = this.secondGraphDefinition;
    //   this.redSeqDef = this.secondGraphDefinition;
    //   this.blueSeqDef = this.secondGraphDefinition;
    //   this.updateSeq()
    // }, 10000);

  }

  constructor() {
  }

  updateSeq() {

    const elementGreen: any = this.mermaidDivGreen.nativeElement;
    const elementRed: any = this.mermaidDivRed.nativeElement;
    const elementBlue: any = this.mermaidDivBlue.nativeElement;

    mermaid.render('graphDivGreen', this.greenSeqDef, (svgCode, bindFunctionsGreen) => {
      elementGreen.innerHTML = svgCode;
      if (bindFunctionsGreen !== undefined) {
        bindFunctionsGreen(elementGreen);
      }
    });

    mermaid.render('graphDivRed', this.redSeqDef, (svgCode, bindFunctionsRed: any) => {
      elementRed.innerHTML = svgCode;
      if (bindFunctionsRed !== undefined) {
        bindFunctionsRed(elementRed);
      }
    });

    mermaid.render('graphDivBlue', this.blueSeqDef, (svgCode, bindFunctionsBlue: any) => {
      elementBlue.innerHTML = svgCode;
      if (bindFunctionsBlue !== undefined) {
        bindFunctionsBlue(elementBlue);
      }
    });
  }

}
