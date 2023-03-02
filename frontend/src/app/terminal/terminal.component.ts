import { AfterViewInit, Component, Inject, Input, ViewChild } from '@angular/core';
import { NgTerminal } from 'ng-terminal';
import { data } from 'vis-network';
import { WorldStateService } from '../services/app.worldState.service';
import { ServerAPIService } from '../services/serverAPI.service';

@Component({
  selector: 'app-terminal',
  templateUrl: './terminal.component.html',
  styleUrls: ['./terminal.component.css']
})
export class TerminalComponent implements AfterViewInit {

  @ViewChild('term', { static: false }) child: NgTerminal;

  buffer: string[]
  cmdExecutionMapping: { "cmd": "string" }

  // Variable to store shortLink from api response
  shortLink: string = "";
  loading: boolean = false; // Flag variable
  file: File; // Variable to store file
  @Input() detailData: any = {}

  constructor(private serverAPIService: ServerAPIService, private worldStateService: WorldStateService) {
    this.buffer = []
  }

  // On file Select
  onChange(event: any) {
    this.file = event.target.files[0];
  }

  // OnClick of button Upload
  onUpload() {
    this.loading = !this.loading;
    this.serverAPIService.upload(this.file).subscribe(
      (event: any) => {

        if (typeof (event) === 'object') {

          // Short link via api response
          // this.shortLink = event.link;

          this.loading = false; // Flag variable 
        }
      }
    );
  }

  ngAfterViewInit() {

    this.child.setRows(11);
    this.child.setCols(102);
    this.child.setDraggable(false)
    this.child.setMinHeight(0);
    this.child.setMinWidth(0);

    this.child.onData().subscribe((input) => {
      if (input === '\r') { // Carriage Return (When Enter is pressed)
        this.child.write("\n\r");
        let cmd = this.buffer.join("").split(" ")
        console.log("entered command:" + cmd); // command to send to the backend

        if (cmd[0] == "clear") {
          this.child.underlying.clear()
        }
        this.buffer = [];

        if (cmd[0] == "ls") {
          let path = ""
          if (cmd.length == 2) {
            path = cmd[1]
          }
          this.serverAPIService.getRequest("worldStateList?path=" + path).subscribe((data: any[]) => {
            if (data.length > 0) {
              if (Object.keys(data[0]).includes("error")) {
                this.child.write(data[0]["error"])
              }
            }

            this.child.write("==========\n\r")
            data.forEach((element: string) => {
              if (("" + element).includes(".")) {
                this.child.write(" - ")
              }
              this.child.write(element);
              this.child.write("\r\n");
            })
            this.child.write("==========")
            this.child.write("\r\n");
          })
        }

        if (cmd[0] == "load") {
          if (cmd.length == 2) {
            const filePath = cmd[1]
            this.serverAPIService.getRequest("worldState?filePath=" + filePath).subscribe((data: any) => {
              this.worldStateService.setState(data)
              if (Object.keys(data).includes("error")) {
                this.child.write(data["error"])
              }
            })
          }
        }

        if (cmd[0] == "createExample") {
          this.serverAPIService.getRequest("createExample").subscribe((data: any) => {
            this.worldStateService.setState(data["environment"])
            this.child.write(data["logs"] + "\r\n")
            if (Object.keys(data).includes("error")) {
              this.child.write(data["error"])
            }
          })
        }

        if (cmd[0] == "next") {
          this.serverAPIService.getRequest("nextWorldState").subscribe((data: any) => {
            this.worldStateService.setState(data["environment"])
            this.child.write(data["logs"] + "\r\n")

            this.worldStateService.setLastAgent(data["agentID"])

            this.worldStateService.setLastMetrics(data["metrics"])

            if (Object.keys(data).includes("error")) {
              this.child.write(data["error"])
            }
          })
        }

        if (cmd[0] == "iterate_over") {
          if (cmd.length == 2) {
            let maxIteration: number = +cmd[1]
            this.serverAPIService.getRequest("iterateOverWorldState?maxIteration=" + maxIteration)
              .subscribe((data: any) => {
                if (Object.keys(data).includes("error")) {
                  this.child.write(data["error"])
                }
                this.worldStateService.setState(data["environment"])
                this.worldStateService.setLastAgent(data["agentID"])
                this.worldStateService.setLastMetrics(data["metrics"])
                this.child.write(data["logs"].join("\r\n") + "\r\n")
              })
          }
        }

        if (cmd[0] == "save") {
          if (cmd.length == 2) {
            const filePath = cmd[1]
            this.serverAPIService.postRequest("saveWorldState?filePath=" + filePath, this.detailData).subscribe((data: any) => {
            })
          }
        }

        if (cmd[0] == "delete") {
          if (cmd.length == 2) {
            const filePath = cmd[1]
            this.serverAPIService.deleteRequest("worldState?filePath=" + filePath).subscribe((data: any) => {
            })
          }
        }

      } else if (input === '\u007f') { // Delete (When Backspace is pressed)
        if (this.child.underlying.buffer.active.cursorX > 0) {
          this.child.write('\b \b');
          this.buffer.pop()
        }
      } else if (input === '\u0003') { // End of Text (When Ctrl and C are pressed)
        this.child.write('^C\n\r');
        this.buffer = [];
      } else {
        this.child.write(input);
        this.buffer.push(input);
      }
    });

  }

  dealWithCommand(cmd: string) {
    return
  }

}