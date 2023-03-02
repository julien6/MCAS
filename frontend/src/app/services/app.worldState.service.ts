import { Injectable } from "@angular/core";
import { BehaviorSubject } from 'rxjs';

@Injectable()
export class WorldStateService {

  private initialNetworkGraph: any = {
    "nodes": [],
    "edges": []
  }

  private networkGraph$ = new BehaviorSubject<any>(this.initialNetworkGraph);
  currentNetworkGraph$ = this.networkGraph$.asObservable();

  private lastAgent$ = new BehaviorSubject<any>("");
  currentLastAgent$ = this.lastAgent$.asObservable();

  private lastMetrics$ = new BehaviorSubject<any>({});
  currentLastMetrics$ = this.lastMetrics$.asObservable();

  constructor() {
  }

  public getInitialState() {
    return this.initialNetworkGraph;
  }

  public setState(worldState: any) {
    this.networkGraph$.next(worldState);
  }

  public setLastAgent(lastAgent: string) {
    this.lastAgent$.next(lastAgent);
  }

  public setLastMetrics(lastMetrics: any) {
    this.lastMetrics$.next(lastMetrics);
  }

}
