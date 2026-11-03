export type QuestState = "available" | "collecting" | "deliver" | "complete";
export class Quest {
  state: QuestState = "available";
  collected = new Set<string>();
  score = 0;
  elapsed = 0;
  accept() {
    if (this.state !== "available") return false;
    this.state = "collecting";
    return true;
  }
  collect(id: string) {
    if (
      this.state !== "collecting" ||
      !["tea", "pier", "garden"].includes(id) ||
      this.collected.has(id)
    )
      return false;
    this.collected.add(id);
    this.score += 25;
    if (this.collected.size === 3) this.state = "deliver";
    return true;
  }
  deliver() {
    if (this.state !== "deliver") return false;
    this.state = "complete";
    this.score += 75;
    return true;
  }
  update(dt: number) {
    if (this.state === "collecting" || this.state === "deliver")
      this.elapsed += dt;
  }
  get instruction() {
    return {
      available: "找阿澄，接下港邊的委託",
      collecting: `收集三枚街區印記　${this.collected.size} / 3`,
      deliver: "將散策手帖交給書店的阿青",
      complete: "港邊委託完成。慢慢走，再看看海。",
    }[this.state];
  }
}
