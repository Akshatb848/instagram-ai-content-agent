import { readdir, readFile } from "node:fs/promises";
const directory = new URL("../n8n/workflows/", import.meta.url);
const files = (await readdir(directory)).filter((name) => name.endsWith(".json"));
if (files.length !== 10) throw new Error(`Expected 10 workflows, found ${files.length}`);
for (const file of files) {
  const workflow = JSON.parse(await readFile(new URL(file, directory), "utf8"));
  if (!workflow.name || !Array.isArray(workflow.nodes) || !workflow.connections) throw new Error(`Invalid workflow: ${file}`);
  const serialized = JSON.stringify(workflow);
  if (/token|password|api[_-]?key/i.test(serialized) && !/\$env|credentials/i.test(serialized)) throw new Error(`Possible embedded secret: ${file}`);
}
console.log(`Validated ${files.length} secret-free workflow exports.`);

