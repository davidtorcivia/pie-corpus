import Foundation
import Vision
import AppKit
// usage: ocr <image> [langs comma-separated]
let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
let langs = args.count > 2 ? args[2].components(separatedBy: ",") : ["de-DE", "en-US"]
guard let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = langs
let h = VNImageRequestHandler(cgImage: cg, options: [:])
try h.perform([req])
for o in (req.results ?? []) { if let t = o.topCandidates(1).first { print(t.string) } }
